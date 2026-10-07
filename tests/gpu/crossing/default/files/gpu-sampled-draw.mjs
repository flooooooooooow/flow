// Browser WebGPU host for the typed sampled vertex/fragment shaders emitted
// from lib/stdlib/gpu_stage_codegen.flow (#811). Unlike shader emission,
// this creates a real render pipeline, draws and reads pixels back.
// Scope: 2D/cubemap RGBA8 textures, triangle/line indexed or nonindexed
// geometry, instances, optional depth32float and MSAA resolve.

function requiredPositive(n, label) {
    if (!Number.isSafeInteger(n) || n <= 0) {
        throw new RangeError(label + " must be a positive safe integer");
    }
    return n;
}

function readLimit(device, name, fallback) {
    const value = device?.limits?.[name];
    return Number.isSafeInteger(value) && value > 0 ? value : fallback;
}

async function verifyShader(module, label) {
    const info = await module.getCompilationInfo();
    const messages = info.messages.filter(m => m.type === "error");
    if (messages.length) {
        throw new Error("WGSL compile failed (" + label + "): " +
            messages.map(m => m.lineNum + ": " + m.message).join("; "));
    }
}

function validateDraw(device, desc) {
    const width = requiredPositive(desc.width, "target width");
    const height = requiredPositive(desc.height, "target height");
    const texWidth = requiredPositive(desc.textureWidth, "textureWidth");
    const texHeight = requiredPositive(desc.textureHeight, "textureHeight");
    if (width > readLimit(device, "maxTextureDimension2D", 8192) ||
        height > readLimit(device, "maxTextureDimension2D", 8192) ||
        texWidth > readLimit(device, "maxTextureDimension2D", 8192) ||
        texHeight > readLimit(device, "maxTextureDimension2D", 8192)) {
        throw new RangeError("texture size exceeds WebGPU device limits");
    }
    const cube = desc.cube === true;
    const layers = cube ? 6 : 1;
    const pixels = desc.textureRGBA;
    const expected = texWidth * texHeight * layers * 4;
    if (!(pixels instanceof Uint8Array) || pixels.length !== expected) {
        throw new TypeError("textureRGBA must contain the complete rgba8unorm image/cube");
    }
    if (!(desc.positions instanceof Float32Array) ||
        desc.positions.length < 12 ||
        desc.positions.length % 4 !== 0) {
        throw new TypeError("positions must contain float4 vertices");
    }
    const vertexCount = desc.positions.length / 4;
    const instances = requiredPositive(desc.instances ?? 1, "instance count");
    const firstInstance = desc.firstInstance ?? 0;
    if (!Number.isSafeInteger(firstInstance) || firstInstance < 0 ||
        firstInstance + instances > 0xffffffff) {
        throw new RangeError("instance range overflow");
    }

    const topology = desc.topology ?? "triangle-list";
    if (!["triangle-list", "line-list"].includes(topology)) {
        throw new TypeError("unsupported render primitive topology");
    }
    const samples = desc.samples ?? 1;
    // The portable WebGPU texture/sample-count contract guarantees 1 and 4;
    // other multisample counts must be negotiated explicitly in the future.
    if (![1, 4].includes(samples)) {
        throw new RangeError("unsupported WebGPU MSAA sample count");
    }
    const indices = desc.indices;
    if (indices !== undefined) {
        if (!(indices instanceof Uint16Array || indices instanceof Uint32Array) ||
            indices.length === 0) {
            throw new TypeError("indices must be a nonempty u16 or u32 index buffer");
        }
        for (const index of indices) {
            if (index >= vertexCount) {
                throw new RangeError("index refers outside the position buffer");
            }
        }
    }
    const count = indices ? indices.length : vertexCount;
    if (topology === "triangle-list" && count % 3 !== 0) {
        throw new RangeError("triangle-list draw requires triples of vertices");
    }
    if (topology === "line-list" && count % 2 !== 0) {
        throw new RangeError("line-list draw requires vertex pairs");
    }
    const sampler = desc.sampler ?? {};
    const filters = [sampler.minFilter ?? "linear", sampler.magFilter ?? "linear"];
    if (filters.some(f => !["linear", "nearest"].includes(f))) {
        throw new TypeError("sampler filter must be linear or nearest");
    }
    const address = [sampler.addressModeU ?? "clamp-to-edge",
                     sampler.addressModeV ?? "clamp-to-edge",
                     sampler.addressModeW ?? "clamp-to-edge"];
    if (address.some(a => !["clamp-to-edge", "repeat"].includes(a))) {
        throw new TypeError("sampler address mode must be clamp-to-edge or repeat");
    }
    if (typeof desc.wgsl !== "string" || !desc.wgsl.trim()) {
        throw new TypeError("a Flow-generated WGSL vertex/fragment module is required");
    }
    const maxBufferSize = readLimit(device,"maxBufferSize",268435456);
    const maxBindingSize = readLimit(device,"maxStorageBufferBindingSize",134217728);
    const indexBytes = indices ? Math.ceil(indices.byteLength/4)*4 : 0;
    const readbackStride = Math.ceil(width*4/256)*256;
    if (desc.positions.byteLength > maxBufferSize ||
        desc.positions.byteLength > maxBindingSize ||
        indexBytes > maxBufferSize ||
        readbackStride*height > maxBufferSize) {
        throw new RangeError("Flow sampled geometry exceeds device buffer capacity");
    }
    return {width,height,texWidth,texHeight,layers,cube,pixels,
            instances,firstInstance,topology,samples,indices,count,sampler,
            indexBytes,readbackStride};
}

/**
 * Render a Flow-generated sampled pipeline and read back exact rgba8 bytes.
 *
 * Descriptor is validated BEFORE GPU allocation. A successful result proves
 * WebGPU device submission and output; comparing to upstream vgpu reference
 * pixels is the caller's independent responsibility.
 */
export async function renderFlowSampledDraw(device, descriptor) {
    if (!device || typeof device.createRenderPipeline !== "function" ||
        !device.queue || typeof device.queue.submit !== "function") {
        throw new TypeError("a live WebGPU render device is required");
    }
    const d = validateDraw(device, descriptor);
    const owned = [];
    const t0 = typeof performance === "object" ? performance.now() : Date.now();
    let readback = null;

    try {
        const shader = device.createShaderModule({
            code:descriptor.wgsl,label:"Flow sampled geometry"
        });
        await verifyShader(shader, "Flow sampled geometry");

        const positionBuffer = device.createBuffer({
            size:descriptor.positions.byteLength,
            usage:GPUBufferUsage.STORAGE | GPUBufferUsage.COPY_DST,
            label:"Flow position stream"
        });
        owned.push(positionBuffer);
        device.queue.writeBuffer(positionBuffer,0,descriptor.positions);

        let indexBuffer = null;
        if (d.indices) {
            // WebGPU buffer size and queue.writeBuffer length are 4-byte
            // aligned. Three u16 indices occupy 6 bytes: pad to 8 without
            // changing the logical drawIndexed count.
            indexBuffer = device.createBuffer({
                size:d.indexBytes,
                usage:GPUBufferUsage.INDEX | GPUBufferUsage.COPY_DST,
                label:"Flow index buffer"
            });
            owned.push(indexBuffer);
            const indexUpload = new Uint8Array(d.indexBytes);
            indexUpload.set(new Uint8Array(
                d.indices.buffer,d.indices.byteOffset,d.indices.byteLength
            ));
            device.queue.writeBuffer(indexBuffer,0,indexUpload);
        }

        const sampledTexture = device.createTexture({
            size:{width:d.texWidth,height:d.texHeight,depthOrArrayLayers:d.layers},
            dimension:"2d",format:"rgba8unorm",
            usage:GPUTextureUsage.TEXTURE_BINDING | GPUTextureUsage.COPY_DST,
            label:"Flow sampled source"
        });
        owned.push(sampledTexture);
        const bytesPerRow = d.texWidth*4;
        const bytesPerFace = bytesPerRow*d.texHeight;
        for (let layer=0;layer<d.layers;layer++) {
            device.queue.writeTexture(
                {texture:sampledTexture, origin:{x:0,y:0,z:layer}},
                d.pixels.subarray(layer*bytesPerFace,(layer+1)*bytesPerFace),
                {bytesPerRow,rowsPerImage:d.texHeight},
                {width:d.texWidth,height:d.texHeight,depthOrArrayLayers:1}
            );
        }

        const texSampler = device.createSampler({
            magFilter:d.sampler.magFilter ?? "linear",
            minFilter:d.sampler.minFilter ?? "linear",
            addressModeU:d.sampler.addressModeU ?? "clamp-to-edge",
            addressModeV:d.sampler.addressModeV ?? "clamp-to-edge",
            addressModeW:d.sampler.addressModeW ?? "clamp-to-edge"
        });
        const pipeline = device.createRenderPipeline({
            layout:"auto",
            vertex:{module:shader,entryPoint:"scene_vs"},
            fragment:{
                module:shader,entryPoint:"scene_fs",
                targets:[{format:"rgba8unorm"}]
            },
            primitive:{topology:d.topology},
            depthStencil:descriptor.depth
                ? {format:"depth32float",depthWriteEnabled:true,depthCompare:"less"}
                : undefined,
            multisample:{count:d.samples}
        });
        const group = device.createBindGroup({
            layout:pipeline.getBindGroupLayout(0),
            entries:[
                {binding:0,resource:{buffer:positionBuffer}},
                {binding:1,resource:sampledTexture.createView(
                    d.cube ? {dimension:"cube"} : {dimension:"2d"}
                )},
                {binding:2,resource:texSampler}
            ]
        });

        const target = device.createTexture({
            size:{width:d.width,height:d.height,depthOrArrayLayers:1},
            format:"rgba8unorm",
            usage:GPUTextureUsage.RENDER_ATTACHMENT | GPUTextureUsage.COPY_SRC,
            label:"Flow resolved color output"
        });
        owned.push(target);

        let colorView = target.createView();
        let resolveTarget = undefined;
        if (d.samples > 1) {
            const msaa = device.createTexture({
                size:{width:d.width,height:d.height,depthOrArrayLayers:1},
                format:"rgba8unorm",
                sampleCount:d.samples,
                usage:GPUTextureUsage.RENDER_ATTACHMENT,
                label:"Flow multisample color"
            });
            owned.push(msaa);
            colorView = msaa.createView();
            resolveTarget = target.createView();
        }

        let depthView = undefined;
        if (descriptor.depth === true) {
            const depth = device.createTexture({
                size:{width:d.width,height:d.height,depthOrArrayLayers:1},
                format:"depth32float", sampleCount:d.samples,
                usage:GPUTextureUsage.RENDER_ATTACHMENT,
                label:"Flow depth attachment"
            });
            owned.push(depth);
            depthView = depth.createView();
        }

        const paddedRowBytes = d.readbackStride;
        readback = device.createBuffer({
            size:paddedRowBytes*d.height,
            usage:GPUBufferUsage.COPY_DST | GPUBufferUsage.MAP_READ,
            label:"Flow sampled draw readback"
        });
        owned.push(readback);

        const encoder = device.createCommandEncoder();
        const pass = encoder.beginRenderPass({
            colorAttachments:[{
                view:colorView, resolveTarget,
                clearValue:{r:0,g:0,b:0,a:1},
                loadOp:"clear",storeOp:"store"
            }],
            depthStencilAttachment:depthView ? {
                view:depthView,depthClearValue:1,
                depthLoadOp:"clear",depthStoreOp:"store"
            } : undefined
        });
        pass.setPipeline(pipeline);
        pass.setBindGroup(0,group);
        if (d.indices) {
            pass.setIndexBuffer(indexBuffer,d.indices instanceof Uint16Array
                ? "uint16" : "uint32");
            pass.drawIndexed(d.count,d.instances,0,0,d.firstInstance);
        } else {
            pass.draw(d.count,d.instances,0,d.firstInstance);
        }
        pass.end();
        encoder.copyTextureToBuffer(
            {texture:target},
            {buffer:readback,bytesPerRow:paddedRowBytes,rowsPerImage:d.height},
            {width:d.width,height:d.height,depthOrArrayLayers:1}
        );
        device.queue.submit([encoder.finish()]);
        await device.queue.onSubmittedWorkDone();

        await readback.mapAsync(GPUMapMode.READ);
        const padded = new Uint8Array(readback.getMappedRange());
        const rgba = new Uint8Array(d.width*d.height*4);
        for(let row=0;row<d.height;row++){
            rgba.set(padded.subarray(row*paddedRowBytes,
                    row*paddedRowBytes+d.width*4),row*d.width*4);
        }
        readback.unmap();
        return {
            rgba,width:d.width,height:d.height,
            instances:d.instances,indexed:!!d.indices,
            elapsedMs:(typeof performance === "object" ? performance.now() : Date.now())-t0,
            execution:"webgpu-device"
        };
    } finally {
        for(const resource of owned)resource.destroy();
    }
}
