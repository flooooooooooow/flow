// Multi-pass execution of WGSL kernels and reflection emitted by Flow.
// GPU buffers persist through all passes: no per-stage upload/readback (#814).
// The output is a live-device result only after submission and mapAsync.
function limit(device, key, fallback) {
    const n=device?.limits?.[key];
    return Number.isSafeInteger(n) && n>0 ? n : fallback;
}

function reflected(x) {
    const k=typeof x==="string" ? JSON.parse(x) : x;
    if (!k || typeof k.entryPoint!=="string" ||
        !/^[A-Za-z_][A-Za-z0-9_]*$/.test(k.entryPoint) ||
        !Array.isArray(k.buffers) || !Array.isArray(k.params) ||
        !Number.isSafeInteger(k.workgroupSize) || k.workgroupSize<=0 ||
        k.workgroupSize>256) {
        throw new TypeError("invalid Flow GPU kernel reflection");
    }
    return k;
}

function packParams(kernel, values) {
    if (kernel.params.length===0) return null;
    if (!Number.isSafeInteger(kernel.paramsBinding) ||
        !Number.isSafeInteger(kernel.paramsBytes) ||
        kernel.paramsBytes<16 || kernel.paramsBytes%16!==0) {
        throw new TypeError("invalid Flow uniform reflection");
    }
    const raw=new ArrayBuffer(kernel.paramsBytes);
    const view=new DataView(raw);
    for(let i=0;i<kernel.params.length;i++){
        const p=kernel.params[i],n=values[p.name];
        if (!Number.isFinite(n) || (i+1)*4>raw.byteLength) {
            throw new TypeError("missing or invalid Flow kernel scalar "+p.name);
        }
        if(p.type==="f32")view.setFloat32(i*4,n,true);
        else if(p.type==="u32")view.setUint32(i*4,n,true);
        else if(p.type==="i32")view.setInt32(i*4,n,true);
        else throw new TypeError("unsupported Flow uniform dtype");
    }
    return raw;
}

function prepare(device,config) {
    if (!config || !config.resources || !Array.isArray(config.passes) ||
        !Array.isArray(config.readback) || !config.passes.length ||
        !config.readback.length) {
        throw new TypeError("Flow GPU graph requires resources, passes and readback");
    }
    const sizes=new Map();
    const maxBytes=Math.min(limit(device,"maxBufferSize",268435456),
        limit(device,"maxStorageBufferBindingSize",134217728));
    for(const [name,value] of Object.entries(config.resources)){
        if(!/^[A-Za-z_][A-Za-z0-9_]*$/.test(name)){
            throw new TypeError("invalid Flow GPU resource name");
        }
        const n=value instanceof Float32Array ? value.length : value;
        if(!Number.isSafeInteger(n) || n<=0 || n>maxBytes/4){
            throw new RangeError("invalid Flow GPU resource size: "+name);
        }
        sizes.set(name,n);
    }
    const ready=[];
    const initialised=new Set(Object.entries(config.resources)
        .filter(([,value])=>value instanceof Float32Array)
        .map(([name])=>name));
    for(const pass of config.passes){
        const kernel=reflected(pass.reflection);
        const n=pass.dispatchElements;
        const wg=kernel.workgroupSize;
        if(typeof pass.wgsl!=="string" || !pass.wgsl.trim() ||
           !Number.isSafeInteger(n) || n<=0 ||
           wg>limit(device,"maxComputeInvocationsPerWorkgroup",256) ||
           wg>limit(device,"maxComputeWorkgroupSizeX",256) ||
           Math.ceil(n/wg)>limit(device,"maxComputeWorkgroupsPerDimension",65535)) {
            throw new RangeError("invalid Flow GPU dispatch");
        }
        const bindings=[];
        const written=new Set();
        const used=new Set();
        const translate=pass.bindings??{};
        for(const b of kernel.buffers){
            const key=translate[b.name]??b.name;
            if(!sizes.has(key) || !Number.isSafeInteger(b.binding) ||
               b.binding<0 || used.has(b.binding) ||
               !["read","write","read_write"].includes(b.access)) {
                throw new TypeError("invalid Flow GPU buffer binding "+b.name);
            }
            const required=pass.requiredElements?.[b.name]??n;
            if(!Number.isSafeInteger(required) || required<=0 ||
               required>sizes.get(key)){
                throw new RangeError("Flow tensor shape exceeds GPU buffer "+key);
            }
            if(b.access!=="write" && !initialised.has(key)){
                throw new Error("GPU resource read before write: "+key);
            }
            if((b.access==="write" || b.access==="read_write") &&
               bindings.some(x=>x.key===key) && pass.feedback!==true) {
                throw new Error("same-pass GPU read/write hazard: "+key);
            }
            if(b.access!=="read")written.add(key);
            used.add(b.binding);
            bindings.push({binding:b.binding,key});
        }
        const uniforms=packParams(kernel,pass.scalars??{});
        if(uniforms){
            if(used.has(kernel.paramsBinding))
                throw new TypeError("uniform binding overlaps GPU buffer");
            used.add(kernel.paramsBinding);
        }
        for(const key of written)initialised.add(key);
        ready.push({kernel,wg,n,wgsl:pass.wgsl,bindings,uniforms});
    }
    for(const name of config.readback){
        if(!sizes.has(name))throw new TypeError("unknown GPU readback resource "+name);
    }
    return {sizes,ready};
}

export async function runFlowGpuPasses(device,config) {
    if(!device || typeof device.createComputePipeline!=="function" ||
       !device.queue || typeof device.queue.submit!=="function"){
        throw new TypeError("a live WebGPU compute device is required");
    }
    const {sizes,ready}=prepare(device,config);
    const handles=new Map(),owned=[],mapped=[];
    const t0=typeof performance==="object" ? performance.now() : Date.now();
    try {
        for(const [name,n] of sizes){
            const buffer=device.createBuffer({
                size:n*4,
                usage:GPUBufferUsage.STORAGE|GPUBufferUsage.COPY_DST|
                    GPUBufferUsage.COPY_SRC,
                label:"Flow graph "+name
            });
            owned.push(buffer);
            handles.set(name,buffer);
            const value=config.resources[name];
            if(value instanceof Float32Array)
                device.queue.writeBuffer(buffer,0,value);
        }

        const encoder=device.createCommandEncoder();
        for(const pass of ready){
            const shader=device.createShaderModule({code:pass.wgsl,
                label:"Flow "+pass.kernel.entryPoint});
            const info=await shader.getCompilationInfo();
            const errors=info.messages.filter(x=>x.type==="error");
            if(errors.length){
                throw new Error("Flow WGSL compilation failed: "+
                    errors.map(x=>x.message).join("; "));
            }
            const pipeline=device.createComputePipeline({
                layout:"auto",
                compute:{module:shader,entryPoint:pass.kernel.entryPoint}
            });
            const entries=pass.bindings.map(b=>({
                binding:b.binding,
                resource:{buffer:handles.get(b.key)}
            }));
            if(pass.uniforms){
                const uniform=device.createBuffer({
                    size:pass.uniforms.byteLength,
                    usage:GPUBufferUsage.UNIFORM|GPUBufferUsage.COPY_DST,
                    label:"Flow graph parameters"
                });
                owned.push(uniform);
                device.queue.writeBuffer(uniform,0,pass.uniforms);
                entries.push({
                    binding:pass.kernel.paramsBinding,
                    resource:{buffer:uniform}
                });
            }
            const group=device.createBindGroup({
                layout:pipeline.getBindGroupLayout(0),entries
            });
            const p=encoder.beginComputePass();
            p.setPipeline(pipeline);
            p.setBindGroup(0,group);
            p.dispatchWorkgroups(Math.ceil(pass.n/pass.wg));
            p.end();
        }
        const stages=new Map();
        for(const name of config.readback){
            const staging=device.createBuffer({
                size:sizes.get(name)*4,
                usage:GPUBufferUsage.COPY_DST|GPUBufferUsage.MAP_READ,
                label:"Flow graph readback "+name
            });
            owned.push(staging);
            encoder.copyBufferToBuffer(handles.get(name),0,staging,0,
                sizes.get(name)*4);
            stages.set(name,staging);
        }
        device.queue.submit([encoder.finish()]);
        await device.queue.onSubmittedWorkDone();
        const outputs={};
        for(const [name,staging] of stages){
            await staging.mapAsync(GPUMapMode.READ);
            mapped.push(staging);
            const bytes=staging.getMappedRange();
            outputs[name]=new Float32Array(bytes.slice(0));
            staging.unmap();
            mapped.pop();
        }
        const elapsedMs=(typeof performance==="object" ? performance.now() :
            Date.now())-t0;
        return {outputs,elapsedMs,passes:ready.length,
            intermediateCpuCopies:0,execution:"webgpu-device"};
    } finally {
        for(const b of mapped){try{b.unmap();}catch{}}
        for(const b of owned){try{b.destroy();}catch{}}
    }
}
