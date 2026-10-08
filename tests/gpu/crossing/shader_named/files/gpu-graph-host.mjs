// Execute a Flow-exported GPU graph on a real WebGPU device (#812).
// Input schema is emitted by lib/stdlib/gpu_graph_export.flow.
// Missing read/write storage texture support is an explicit failure.
// No CPU roundtrips between passes; one final RGBA readback.

const FORMATS={1:["r32float",4],2:["rg32float",8],3:["rgba16float",8],4:["rgba8unorm",4]};
function checkInt(v,what,min=0,max=Number.MAX_SAFE_INTEGER) {
    if(!Number.isSafeInteger(v)||v<min||v>max)
        throw new RangeError(what+" outside supported bounds");
    return v;
}
function validate(device,graph,width,height) {
    if(!graph||graph.schema!=="flow-gpu-graph/1"||
       graph.hazardMode!==0||
       !Array.isArray(graph.resources)||!Array.isArray(graph.passes)||
       !Array.isArray(graph.deps)||!Array.isArray(graph.pingpongs))
        throw new TypeError("expected strict Flow GPU graph export v1");
    if(typeof navigator==="undefined" ||
       !navigator.gpu?.wgslLanguageFeatures?.has("readonly_and_readwrite_storage_textures"))
        throw new Error("WebGPU device lacks readonly_and_readwrite_storage_textures");
    checkInt(width,"render width",1,device.limits?.maxTextureDimension2D??8192);
    checkInt(height,"render height",1,device.limits?.maxTextureDimension2D??8192);
    if(graph.resources.length>16||!graph.resources.length||
       graph.passes.length>16||!graph.passes.length)
        throw new RangeError("graph exceeds Flow resource/pass limits");
    const ids=new Map();
    for(const r of graph.resources) {
        checkInt(r.id,"resource id",0,15);
        checkInt(r.physical,"physical id",0,15);
        if(ids.has(r.id)||![1,2].includes(r.kind))throw new Error("invalid resource ID/kind");
        if(r.kind===1) {
            checkInt(r.bytes,"storage buffer bytes",4,device.limits?.maxStorageBufferBindingSize??104857600);
            if(r.bytes%4!==0)throw new Error("storage buffers need 4-byte aligned length");
        } else {
            if(!FORMATS[r.format]||r.dim!==2||r.depth!==1)
                throw new Error("only 2D storage texture formats supported");
            checkInt(r.width,"texture width",1,device.limits?.maxTextureDimension2D??8192);
            checkInt(r.height,"texture height",1,device.limits?.maxTextureDimension2D??8192);
        }
        ids.set(r.id,r);
    }
    for(let i=0;i<graph.passes.length;i++) {
        const p=graph.passes[i];
        if(p.id!==i||![1,2].includes(p.kind)||!Array.isArray(p.bindings)||
           p.bindings.length>8||!Array.isArray(p.dispatch)||
           !Array.isArray(p.workgroup)||p.dispatch.length!==3||
           p.workgroup.length!==3||typeof p.wgsl!=="string"||!p.wgsl)
            throw new TypeError("invalid Flow pass");
        checkInt(p.iterations,"iteration count",1,1024);
        if(p.feedback!==0||p.workgroupBytes>0||p.barrier>0)
            throw new Error("unsupported feedback/workgroup memory in WebGPU host");
        const usedSlots=new Set(),phys=new Set();
        for(const b of p.bindings) {
            checkInt(b.slot,"binding slot",0,7);
            if(usedSlots.has(b.slot)||!ids.has(b.resourceId))
                throw new Error("duplicate slot or missing bound resource");
            usedSlots.add(b.slot);
            checkInt(b.usage,"access",1,3);
            const physical=ids.get(b.resourceId).physical;
            if(phys.has(physical))
                throw new Error("same physical resource bound more than once");
            phys.add(physical);
        }
        if(p.kind===1) {
            let threads=1;
            for(let k=0;k<3;k++) {
                checkInt(p.workgroup[k],"workgroup",1,256);
                checkInt(p.dispatch[k],"dispatch",1,2147483647);
                threads*=p.workgroup[k];
            }
            if(threads>256)throw new RangeError("workgroup exceeds 256 threads");
        } else if(p.iterations!==1)throw new Error("render repeats unsupported");
    }
    for(const [from,to] of graph.deps) {
        checkInt(from,"source pass",0,graph.passes.length-1);
        checkInt(to,"destination pass",0,graph.passes.length-1);
        if(from>=to)throw new Error("nonforward graph dependency");
    }
    return ids;
}
async function compiled(device,code,name) {
    const module=device.createShaderModule({code,label:name});
    const info=await module.getCompilationInfo();
    const errs=info.messages.filter(m=>m.type==="error");
    if(errs.length)throw new Error("Flow WGSL compile failed for "+name+": "+
        errs.map(m=>m.message).join("; "));
    return module;
}
const FULLSCREEN_VERT=`
@vertex fn flow_graph_vertex(@builtin(vertex_index) v:u32)->@builtin(position) vec4<f32>{
 let points=array<vec2<f32>,3>(vec2<f32>(-1.0,-1.0),vec2<f32>(3.0,-1.0),vec2<f32>(-1.0,3.0));
 return vec4<f32>(points[v],0.0,1.0);
}
`;
const STORAGE_ACCESS={1:"read-only",2:"write-only",3:"read-write"};
// Explicit bind group layout for one pass, built from its typed bindings.
function bindGroupLayout(device,p,ids) {
    const visibility=p.kind===1?GPUShaderStage.COMPUTE:GPUShaderStage.FRAGMENT;
    return device.createBindGroupLayout({label:"Flow "+p.name,entries:p.bindings.map(b=>{
        const r=ids.get(b.resourceId);
        if(r.kind===1)return {binding:b.slot,visibility,
            buffer:{type:b.usage===1?"read-only-storage":"storage"}};
        return {binding:b.slot,visibility,storageTexture:{
            access:STORAGE_ACCESS[b.usage],format:FORMATS[r.format][0],viewDimension:"2d"}};
    })});
}
function bindId(graph,b,iteration) {
    if(iteration%2===0||b.pingpongId<0)return b.resourceId;
    const pp=graph.pingpongs.find(p=>p.id===b.pingpongId);
    if(!pp)throw new Error("missing pingpong pair");
    if(b.resourceId===pp.a)return pp.b;
    if(b.resourceId===pp.b)return pp.a;
    throw new Error("binding is outside pingpong pair");
}
/**
 * Runs Flow-generated storage-compute and fullscreen render stages.
 * initialResources maps resource IDs to raw Uint8Array bytes. The function
 * returns GPU-executed RGBA pixels only after queue and map completion.
 */
export async function runFlowWebGpuGraph(device,graph,{width=64,height=64,initialResources={}}={}) {
    if(!device?.queue||!device.createCommandEncoder||
       !device.createComputePipelineAsync)
        throw new TypeError("live WebGPU device with compute pipeline required");
    const ids=validate(device,graph,width,height);
    const phys=new Map(),byId=new Map(),owned=[];
    const t0=typeof performance==="object"?performance.now():Date.now();
    try {
        for(const r of graph.resources) {
            if(phys.has(r.physical)) {
                const old=phys.get(r.physical).desc;
                if(old.kind!==r.kind||old.bytes!==r.bytes||
                   old.format!==r.format||old.width!==r.width||old.height!==r.height)
                    throw new Error("physical alias descriptor mismatch");
            } else {
                let obj;
                if(r.kind===1) {
                    obj=device.createBuffer({
                        size:r.bytes,usage:GPUBufferUsage.STORAGE|
                            GPUBufferUsage.COPY_DST|GPUBufferUsage.COPY_SRC,
                        label:"Flow "+r.name
                    });
                } else {
                    obj=device.createTexture({
                        size:{width:r.width,height:r.height,depthOrArrayLayers:1},
                        format:FORMATS[r.format][0],
                        usage:GPUTextureUsage.STORAGE_BINDING|
                            GPUTextureUsage.TEXTURE_BINDING|
                            GPUTextureUsage.COPY_SRC|GPUTextureUsage.COPY_DST,
                        label:"Flow "+r.name
                    });
                }
                owned.push(obj);
                phys.set(r.physical,{obj,desc:r});
            }
            byId.set(r.id,phys.get(r.physical).obj);
        }
        for(const r of graph.resources) {
            if(phys.get(r.physical).desc.id!==r.id)continue;
            const byteLength=r.kind===1?r.bytes:
                r.width*r.height*FORMATS[r.format][1];
            const bytes=initialResources[r.id]??new Uint8Array(byteLength);
            if(!(bytes instanceof Uint8Array)||bytes.length!==byteLength)
                throw new TypeError("resource "+r.id+" needs "+byteLength+" raw bytes");
            if(r.kind===1)device.queue.writeBuffer(byId.get(r.id),0,bytes);
            else device.queue.writeTexture(
                {texture:byId.get(r.id)},bytes,
                {bytesPerRow:r.width*FORMATS[r.format][1],rowsPerImage:r.height},
                {width:r.width,height:r.height,depthOrArrayLayers:1});
        }
        const pipelines=[],layouts=[];
        for(const p of graph.passes) {
            // The layout comes from the graph bindings, so a binding the
            // shader does not read still has a slot; an "auto" layout would
            // drop it and fail createBindGroup.
            const bgl=bindGroupLayout(device,p,ids);
            layouts.push(bgl);
            const layout=device.createPipelineLayout({bindGroupLayouts:[bgl]});
            // WGSL requires-directives must precede all declarations.
            const mod=await compiled(device,
                p.wgsl+(p.kind===2?FULLSCREEN_VERT:""),p.name);
            if(p.kind===1) {
                pipelines.push(await device.createComputePipelineAsync({
                    layout,compute:{module:mod,entryPoint:p.name}
                }));
            } else {
                const spec={layout,
                    vertex:{module:mod,entryPoint:"flow_graph_vertex"},
                    fragment:{module:mod,entryPoint:p.name,
                              targets:[{format:"rgba8unorm"}]},
                    primitive:{topology:"triangle-list"}};
                pipelines.push(device.createRenderPipelineAsync
                    ? await device.createRenderPipelineAsync(spec)
                    : device.createRenderPipeline(spec));
            }
        }
        const output=device.createTexture({
            size:{width,height,depthOrArrayLayers:1},
            format:"rgba8unorm",
            usage:GPUTextureUsage.RENDER_ATTACHMENT|GPUTextureUsage.COPY_SRC
        });
        owned.push(output);
        const pitch=Math.ceil(width*4/256)*256;
        const readback=device.createBuffer({
            size:pitch*height,usage:GPUBufferUsage.COPY_DST|GPUBufferUsage.MAP_READ
        });
        owned.push(readback);
        const cmd=device.createCommandEncoder();
        let dispatches=0,rendered=false;
        for(let index=0;index<graph.passes.length;index++) {
            const p=graph.passes[index],pipeline=pipelines[index];
            for(let it=0;it<p.iterations;it++) {
                const entries=[],physicalUsed=new Set();
                for(const b of p.bindings) {
                    const rid=bindId(graph,b,it),r=ids.get(rid),obj=byId.get(rid);
                    if(!r||!obj||physicalUsed.has(r.physical))
                        throw new Error("unsafe or absent physical binding");
                    physicalUsed.add(r.physical);
                    entries.push({binding:b.slot,resource:r.kind===1
                        ?{buffer:obj}:obj.createView()});
                }
                const group=device.createBindGroup({
                    layout:layouts[index],entries
                });
                if(p.kind===1) {
                    const pass=cmd.beginComputePass();
                    pass.setPipeline(pipeline);pass.setBindGroup(0,group);
                    const counts=p.dispatch.map((dim,axis)=>
                        Math.ceil(dim/p.workgroup[axis]));
                    if(counts.some(n=>n>(device.limits?.maxComputeWorkgroupsPerDimension??65535)))
                        throw new RangeError("compute dispatch limit");
                    pass.dispatchWorkgroups(...counts);pass.end();dispatches++;
                } else {
                    if(rendered)throw new Error("multiple render targets unsupported");
                    const pass=cmd.beginRenderPass({colorAttachments:[{
                        view:output.createView(),
                        loadOp:"clear",storeOp:"store",
                        clearValue:{r:0,g:0,b:0,a:1}
                    }]});
                    pass.setPipeline(pipeline);pass.setBindGroup(0,group);
                    pass.draw(3);pass.end();rendered=true;
                }
            }
        }
        if(!rendered)throw new Error("graph did not render an output");
        cmd.copyTextureToBuffer({texture:output},
            {buffer:readback,bytesPerRow:pitch,rowsPerImage:height},
            {width,height,depthOrArrayLayers:1});
        device.queue.submit([cmd.finish()]);
        await device.queue.onSubmittedWorkDone();
        await readback.mapAsync(GPUMapMode.READ);
        const mapped=new Uint8Array(readback.getMappedRange());
        const rgba=new Uint8Array(width*height*4);
        for(let y=0;y<height;y++)
            rgba.set(mapped.subarray(y*pitch,y*pitch+width*4),y*width*4);
        readback.unmap();
        return {
            rgba,width,height,computeDispatches:dispatches,
            execution:"webgpu-device",
            elapsedMs:(typeof performance==="object"?performance.now():Date.now())-t0
        };
    } finally {
        for(const obj of owned)obj.destroy();
    }
}
