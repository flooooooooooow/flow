// Generic WebGPU host for Flow GPU kernels and fullscreen FSL shaders.
//
// Compute kernels use the reflection emitted by tools/gpu/main.flow.
// Fullscreen shaders use the fixed ABI emitted by compiler/src/shader_dsl.flow:
//   vertex entry   flow_shader_vertex
//   fragment entry <fill-name>_frag
//   group 0 binding 0 FlowShaderUniforms { time, width, height, pad }

export async function getDevice() {
    if (!navigator.gpu) throw new Error("navigator.gpu missing: this browser has no WebGPU");
    const adapter = await navigator.gpu.requestAdapter();
    if (!adapter) throw new Error("requestAdapter returned null: no WebGPU adapter available");
    const device = await adapter.requestDevice();
    return { adapter, device };
}

async function assertShaderCompiles(module, label) {
    const info = await module.getCompilationInfo();
    const errors = info.messages.filter((m) => m.type === "error");
    if (errors.length) {
        throw new Error(
            "WGSL compile error in " + label + ": " +
            errors.map((m) => `line ${m.lineNum}: ${m.message}`).join("; ")
        );
    }
}

// Pack the kernel's scalar parameters into its uniform block. WGSL requires a
// uniform buffer to be a multiple of 16 bytes, which is why paramsBytes is
// rounded up by the generator.
function packParams(kernel, scalars) {
    const buf = new ArrayBuffer(kernel.paramsBytes);
    const view = new DataView(buf);
    kernel.params.forEach((p, i) => {
        const value = scalars[p.name];
        if (value === undefined) throw new Error(`kernel ${kernel.kernel}: no value for '${p.name}'`);
        const offset = i * 4;
        if (p.type === "f32") view.setFloat32(offset, value, true);
        else if (p.type === "u32") view.setUint32(offset, value, true);
        else view.setInt32(offset, value, true);
    });
    return buf;
}

/**
 * Run one compute kernel.
 *   inputs   {name: Float32Array} for every `read` storage binding
 *   scalars  {name: number} for every uniform parameter
 *   count    elements in each buffer, and the dispatch extent
 * Returns {outputs: {name: Float32Array}, ms}
 */
export async function runKernel(device, kernel, code, inputs, scalars, count) {
    // Validate before allocating. The same host is used for standalone
    // @gpu kernels and IR-generated compute-graph passes.
    if (!device || !device.queue || typeof device.createComputePipeline !== "function" ||
        !Number.isSafeInteger(count) || count < 1 || !kernel ||
        !Array.isArray(kernel.buffers) || !Array.isArray(kernel.params) ||
        !Number.isSafeInteger(kernel.workgroupSize) || kernel.workgroupSize < 1 ||
        typeof code !== "string" || !code.trim()) {
        throw new TypeError("invalid Flow WebGPU compute dispatch");
    }
    const bytes = count * 4;
    const bindingLimit = device?.limits?.maxStorageBufferBindingSize ?? 134217728;
    const bufferLimit = device?.limits?.maxBufferSize ?? 268435456;
    const groupLimit = device?.limits?.maxComputeWorkgroupsPerDimension ?? 65535;
    const groupSizeLimit = device?.limits?.maxComputeInvocationsPerWorkgroup ?? 256;
    if (bytes > bufferLimit || bytes > bindingLimit ||
        kernel.workgroupSize > groupSizeLimit ||
        Math.ceil(count/kernel.workgroupSize) > groupLimit) {
        throw new RangeError("Flow WebGPU dispatch exceeds device limits");
    }
    const seen = new Set();
    for (const b of kernel.buffers) {
        if (!b || typeof b.name !== "string" ||
            !/^[A-Za-z_][A-Za-z0-9_]*$/.test(b.name) ||
            !Number.isSafeInteger(b.binding) || b.binding < 0 ||
            seen.has(b.binding) ||
            !["read","write","read_write"].includes(b.access)) {
            throw new TypeError("invalid Flow GPU buffer reflection");
        }
        seen.add(b.binding);
        if (b.access === "read" &&
            (!(inputs?.[b.name] instanceof Float32Array) ||
             inputs[b.name].length !== count)) {
            throw new TypeError("Flow GPU input must match dispatch extent: "+b.name);
        }
    }
    if (kernel.params.length &&
        (!Number.isSafeInteger(kernel.paramsBinding) ||
         kernel.paramsBinding < 0 || seen.has(kernel.paramsBinding))) {
        throw new TypeError("invalid Flow GPU parameter binding");
    }

    const module = device.createShaderModule({ code, label: kernel.kernel });
    await assertShaderCompiles(module, kernel.kernel);

    const gpuBuffers = {};
    const entries = [];
    const readbackNames = [];
    const staging = {};
    const owned = [];
    const mapped = [];
    const now = () => typeof performance === "object"
        ? performance.now() : Date.now();
    try {
        for (const b of kernel.buffers) {
            if (b.access === "read") {
                const buffer = device.createBuffer({
                    size: bytes,
                    usage: GPUBufferUsage.STORAGE | GPUBufferUsage.COPY_DST,
                    label: b.name,
                });
                owned.push(buffer);
                device.queue.writeBuffer(buffer, 0, inputs[b.name]);
                gpuBuffers[b.name] = buffer;
            } else {
                gpuBuffers[b.name] = device.createBuffer({
                    size: bytes,
                    usage: GPUBufferUsage.STORAGE | GPUBufferUsage.COPY_SRC |
                        GPUBufferUsage.COPY_DST,
                    label: b.name,
                });
                owned.push(gpuBuffers[b.name]);
                readbackNames.push(b.name);
            }
            entries.push({ binding: b.binding, resource: { buffer: gpuBuffers[b.name] } });
        }

        if (kernel.paramsBinding !== null && kernel.params.length) {
            const paramsBuffer = device.createBuffer({
                size: kernel.paramsBytes,
                usage: GPUBufferUsage.UNIFORM | GPUBufferUsage.COPY_DST,
                label: "params",
            });
            owned.push(paramsBuffer);
            device.queue.writeBuffer(paramsBuffer, 0, packParams(kernel, scalars));
            entries.push({ binding: kernel.paramsBinding, resource: { buffer: paramsBuffer } });
        }

        const pipeline = device.createComputePipeline({
            layout: "auto",
            compute: { module, entryPoint: kernel.entryPoint },
        });
        const bindGroup = device.createBindGroup({
            layout: pipeline.getBindGroupLayout(0),
            entries,
        });

        for (const name of readbackNames) {
            staging[name] = device.createBuffer({
                size: bytes,
                usage: GPUBufferUsage.COPY_DST | GPUBufferUsage.MAP_READ,
            });
            owned.push(staging[name]);
        }

        const t0 = now();
        const encoder = device.createCommandEncoder();
        const pass = encoder.beginComputePass();
        pass.setPipeline(pipeline);
        pass.setBindGroup(0, bindGroup);
        pass.dispatchWorkgroups(Math.ceil(count / kernel.workgroupSize));
        pass.end();
        for (const name of readbackNames) {
            encoder.copyBufferToBuffer(gpuBuffers[name], 0, staging[name], 0, bytes);
        }
        device.queue.submit([encoder.finish()]);
        await device.queue.onSubmittedWorkDone();
        const ms = now() - t0;

        const outputs = {};
        for (const name of readbackNames) {
            await staging[name].mapAsync(GPUMapMode.READ);
            mapped.push(staging[name]);
            outputs[name] = new Float32Array(staging[name].getMappedRange().slice(0));
            staging[name].unmap();
            mapped.pop();
        }
        return { outputs, ms };
    } finally {
        for (const buffer of mapped) {
            try { buffer.unmap(); } catch {}
        }
        for (const buffer of owned) {
            try { buffer.destroy(); } catch {}
        }
    }
}

/**
 * Render one generated FSL WGSL fragment entry into an rgba8unorm texture and
 * return tightly packed RGBA bytes. The output does not depend on canvas DPR,
 * browser compositing or swap-chain format, which makes it suitable for exact
 * compatibility tests.
 */
export async function renderFullscreenShader(
    device,
    code,
    fragmentEntry,
    width,
    height,
    { time = 0 } = {},
) {
    if (!Number.isInteger(width) || width <= 0 || !Number.isInteger(height) || height <= 0) {
        throw new Error("width and height must be positive integers");
    }

    const label = fragmentEntry;
    const module = device.createShaderModule({ code, label });
    await assertShaderCompiles(module, label);

    const uniformLayout = device.createBindGroupLayout({
        entries: [{
            binding: 0,
            visibility: GPUShaderStage.VERTEX | GPUShaderStage.FRAGMENT,
            buffer: { type: "uniform" },
        }],
    });
    const pipelineLayout = device.createPipelineLayout({ bindGroupLayouts: [uniformLayout] });
    const pipeline = device.createRenderPipeline({
        layout: pipelineLayout,
        vertex: {
            module,
            entryPoint: "flow_shader_vertex",
        },
        fragment: {
            module,
            entryPoint: fragmentEntry,
            targets: [{ format: "rgba8unorm" }],
        },
        primitive: { topology: "triangle-list" },
    });

    const uniformBuffer = device.createBuffer({
        size: 16,
        usage: GPUBufferUsage.UNIFORM | GPUBufferUsage.COPY_DST,
        label: "FlowShaderUniforms",
    });
    device.queue.writeBuffer(uniformBuffer, 0, new Float32Array([time, width, height, 0]));
    const bindGroup = device.createBindGroup({
        layout: uniformLayout,
        entries: [{ binding: 0, resource: { buffer: uniformBuffer } }],
    });

    const texture = device.createTexture({
        size: { width, height, depthOrArrayLayers: 1 },
        format: "rgba8unorm",
        usage: GPUTextureUsage.RENDER_ATTACHMENT | GPUTextureUsage.COPY_SRC,
        label: label + " output",
    });

    const bytesPerPixel = 4;
    const tightBytesPerRow = width * bytesPerPixel;
    const bytesPerRow = Math.ceil(tightBytesPerRow / 256) * 256;
    const readback = device.createBuffer({
        size: bytesPerRow * height,
        usage: GPUBufferUsage.COPY_DST | GPUBufferUsage.MAP_READ,
        label: label + " readback",
    });

    const t0 = performance.now();
    const encoder = device.createCommandEncoder();
    const pass = encoder.beginRenderPass({
        colorAttachments: [{
            view: texture.createView(),
            clearValue: { r: 0, g: 0, b: 0, a: 1 },
            loadOp: "clear",
            storeOp: "store",
        }],
    });
    pass.setPipeline(pipeline);
    pass.setBindGroup(0, bindGroup);
    pass.draw(3);
    pass.end();

    encoder.copyTextureToBuffer(
        { texture },
        { buffer: readback, bytesPerRow, rowsPerImage: height },
        { width, height, depthOrArrayLayers: 1 },
    );
    device.queue.submit([encoder.finish()]);
    await device.queue.onSubmittedWorkDone();
    const ms = performance.now() - t0;

    await readback.mapAsync(GPUMapMode.READ);
    const padded = new Uint8Array(readback.getMappedRange());
    const rgba = new Uint8Array(tightBytesPerRow * height);
    for (let y = 0; y < height; y++) {
        const src = y * bytesPerRow;
        const dst = y * tightBytesPerRow;
        rgba.set(padded.subarray(src, src + tightBytesPerRow), dst);
    }
    readback.unmap();

    readback.destroy();
    texture.destroy();
    uniformBuffer.destroy();

    return { rgba, width, height, ms };
}

/** Element-wise agreement between a GPU result and a CPU reference. */
export function compare(gpu, cpu) {
    let maxAbs = 0;
    let maxRel = 0;
    let exact = 0;
    let worstIndex = -1;
    for (let i = 0; i < cpu.length; i++) {
        const d = Math.abs(gpu[i] - cpu[i]);
        if (d === 0) exact++;
        if (d > maxAbs) {
            maxAbs = d;
            worstIndex = i;
        }
        const scale = Math.max(Math.abs(cpu[i]), 1e-30);
        if (d / scale > maxRel) maxRel = d / scale;
    }
    return { maxAbs, maxRel, exact, n: cpu.length, worstIndex };
}

/** Byte-for-byte RGBA comparison for deterministic render compatibility cases. */
export function compareRgba(actual, expected) {
    if (actual.length !== expected.length) {
        return {
            exact: false,
            differingBytes: Math.abs(actual.length - expected.length),
            maxChannelError: 255,
            worstIndex: -1,
        };
    }

    let differingBytes = 0;
    let maxChannelError = 0;
    let worstIndex = -1;
    for (let i = 0; i < actual.length; i++) {
        const error = Math.abs(actual[i] - expected[i]);
        if (error !== 0) differingBytes++;
        if (error > maxChannelError) {
            maxChannelError = error;
            worstIndex = i;
        }
    }
    return {
        exact: differingBytes === 0,
        differingBytes,
        maxChannelError,
        worstIndex,
    };
}
