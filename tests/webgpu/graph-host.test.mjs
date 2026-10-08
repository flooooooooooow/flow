// Mock WebGPU execution tests for exported Flow graph contract.
// node --test tests/webgpu/graph-host.test.mjs
import test from "node:test";
import assert from "node:assert/strict";
import {runFlowWebGpuGraph} from "../../wasm/crossing_assets/gpu-graph-host.mjs";

globalThis.GPUBufferUsage={STORAGE:1,COPY_DST:2,COPY_SRC:4,MAP_READ:8};
globalThis.GPUTextureUsage={STORAGE_BINDING:1,TEXTURE_BINDING:2,COPY_SRC:4,COPY_DST:8,RENDER_ATTACHMENT:16};
globalThis.GPUMapMode={READ:1};
globalThis.GPUShaderStage={VERTEX:1,FRAGMENT:2,COMPUTE:4};

function fake({supported=true,compilerErrors=[]}={}){
    // Read/write storage textures are a WGSL *language* feature on navigator.gpu,
    // not a GPUDevice feature requested through requiredFeatures.
    Object.defineProperty(globalThis, "navigator", {
        configurable: true,
        value: {gpu: {wgslLanguageFeatures: new Set(
            supported ? ["readonly_and_readwrite_storage_textures"] : []
        )}}
    });
    const stats={resources:[],groups:[],dispatches:[],draws:0,submits:0,layouts:[],pipelines:[]};
    function buffer(d){
        const b={
            raw:new Uint8Array(d.size),destroyed:false,
            async mapAsync(mode){assert.equal(mode,GPUMapMode.READ)},
            getMappedRange(){return this.raw.buffer},
            unmap(){},destroy(){this.destroyed=true}
        };
        stats.resources.push(b);
        return b;
    }
    function texture(d){
        const t={desc:d,destroyed:false,createView(){return {texture:t}},
            destroy(){this.destroyed=true}};
        stats.resources.push(t);
        return t;
    }
    const device={
        features:new Set(supported?["readonly_and_readwrite_storage_textures"]:[]),
        limits:{
            maxTextureDimension2D:1024,maxStorageBufferBindingSize:65536,
            maxComputeWorkgroupsPerDimension:65535
        },
        createBuffer:buffer,createTexture:texture,
        createShaderModule({code}){
            assert.ok(code.length);
            return {async getCompilationInfo(){return {messages:compilerErrors}}};
        },
        createBindGroupLayout(d){
            stats.layouts.push(d);
            return {entries:d.entries};
        },
        createPipelineLayout({bindGroupLayouts}){
            return {bindGroupLayouts};
        },
        async createComputePipelineAsync({layout,compute}){
            stats.pipelines.push({entry:compute.entryPoint,layout});
            return {entry:compute.entryPoint,getBindGroupLayout(){return {entries:[]}}};
        },
        async createRenderPipelineAsync({layout,fragment}){
            stats.pipelines.push({entry:fragment.entryPoint,layout});
            return {entry:fragment.entryPoint,getBindGroupLayout(){return {entries:[]}}};
        },
        createBindGroup({layout,entries}){
            // WebGPU rejects a bind group whose entry count differs from its layout.
            assert.equal(entries.length,layout.entries.length);
            stats.groups.push(entries);
            return {entries};
        },
        createCommandEncoder(){
            const events=[];
            return {
                beginComputePass(){
                    let entry={};
                    return {
                        setPipeline(p){entry.pipeline=p},
                        setBindGroup(i,g){entry.bindings=g.entries},
                        dispatchWorkgroups(...counts){entry.counts=counts},
                        end(){events.push({kind:"compute",...entry})}
                    };
                },
                beginRenderPass(){
                    return {
                        setPipeline(){},setBindGroup(){},
                        draw(n){assert.equal(n,3);stats.draws++},
                        end(){events.push({kind:"render"})}
                    };
                },
                copyTextureToBuffer(src,dst,size){
                    events.push({kind:"readback",dst,size});
                },
                finish(){return events}
            };
        },
        queue:{
            writeBuffer(b,offset,data){
                const bytes=data instanceof Uint8Array?data:
                    new Uint8Array(data.buffer,data.byteOffset,data.byteLength);
                b.raw.set(bytes,offset);
            },
            writeTexture(){},
            submit(list){
                stats.submits++;
                for(const e of list[0]){
                    if(e.kind==="compute")stats.dispatches.push(e.counts);
                    if(e.kind==="readback"){
                        for(let y=0;y<e.size.height;y++)
                            for(let x=0;x<e.size.width;x++)
                                e.dst.buffer.raw.set([x*13,y*17,255,255],
                                    y*e.dst.bytesPerRow+x*4);
                    }
                }
            },
            async onSubmittedWorkDone(){}
        }
    };
    return {device,stats};
}
function sample(){
    const buffer=(id)=>({
        id,name:"buf"+id,kind:1,physical:id,
        bytes:16,format:0,dim:0,width:0,height:0,depth:0
    });
    const texture={
        id:2,name:"image",kind:2,physical:2,format:4,
        dim:2,width:4,height:4,depth:1,bytes:0
    };
    const bind=(resourceId,slot,pingpongId=-1)=>({
        resourceId,slot,pingpongId,usage:slot===0?1:2,role:slot
    });
    return {
        schema:"flow-gpu-graph/1",hazardMode:0,
        resources:[buffer(0),buffer(1),texture],
        pingpongs:[{id:0,a:0,b:1,front:0}],
        deps:[[0,1,0]],
        passes:[
            {
                id:0,name:"pressure",kind:1,iterations:4,
                drawCount:0,feedback:0,workgroupBytes:0,barrier:0,
                workgroup:[4,1,1],dispatch:[4,1,1],
                wgsl:"@compute @workgroup_size(4) fn pressure() {}",
                bindings:[bind(0,0,0),bind(1,1,0)]
            },
            {
                id:1,name:"display",kind:2,iterations:1,
                drawCount:3,feedback:0,workgroupBytes:0,barrier:0,
                workgroup:[1,1,1],dispatch:[1,1,1],
                wgsl:"@fragment fn display() -> @location(0) vec4<f32> {return vec4<f32>(1.0);}",
                bindings:[{resourceId:2,slot:0,pingpongId:-1,usage:1,role:0}]
            }
        ]
    };
}
test("20-like pingpong dispatches alternate bindings without CPU copies",async()=>{
    const {device,stats}=fake();
    const r=await runFlowWebGpuGraph(device,sample(),{width:4,height:4});
    assert.equal(r.execution,"webgpu-device");
    assert.equal(r.computeDispatches,4);
    assert.equal(stats.submits,1);
    assert.equal(stats.draws,1);
    assert.equal(r.rgba.length,4*4*4);
    assert.deepEqual([...r.rgba.slice(0,4)],[0,0,255,255]);
    assert.deepEqual([...r.rgba.slice(4,8)],[13,0,255,255]);
    assert.deepEqual(stats.dispatches,[[1,1,1],[1,1,1],[1,1,1],[1,1,1]]);
    const first=stats.groups[0],second=stats.groups[1],third=stats.groups[2];
    assert.equal(first[0].resource.buffer,second[1].resource.buffer);
    assert.equal(first[1].resource.buffer,second[0].resource.buffer);
    assert.equal(first[0].resource.buffer,third[0].resource.buffer);
    assert.ok(stats.resources.every(r=>r.destroyed));
});
test("readonly texture feature absence refuses generated shaders",async()=>{
    const {device,stats}=fake({supported:false});
    await assert.rejects(runFlowWebGpuGraph(device,sample()),/readonly_and_readwrite_storage_textures/);
    assert.equal(stats.resources.length,0);
});
test("shader compilation errors are never reported as GPU success",async()=>{
    const {device,stats}=fake({compilerErrors:[{type:"error",message:"bad wgsl"}]});
    await assert.rejects(runFlowWebGpuGraph(device,sample()),/WGSL compile failed/);
    assert.ok(stats.resources.every(r=>r.destroyed));
    assert.equal(stats.submits,0);
});
test("aliasing two binding slots to one resource is rejected",async()=>{
    const {device}=fake();
    const g=sample();
    g.passes[0].bindings[1].resourceId=0;
    await assert.rejects(runFlowWebGpuGraph(device,g),/same physical resource/);
});
test("every typed binding is in an explicit layout, read by the shader or not",async()=>{
    const {device,stats}=fake();
    await runFlowWebGpuGraph(device,sample(),{width:4,height:4});
    // The display fragment never reads its texture. An "auto" layout drops
    // that binding, and the bind group no longer matches it. The fluid
    // display pass binds velocity that it does not read.
    assert.ok(stats.pipelines.every(p=>p.layout!=="auto"));
    assert.deepEqual(stats.layouts[1].entries,[{binding:0,visibility:GPUShaderStage.FRAGMENT,
        storageTexture:{access:"read-only",format:"rgba8unorm",viewDimension:"2d"}}]);
    assert.deepEqual(stats.layouts[0].entries.map(e=>e.buffer.type),["read-only-storage","storage"]);
});
