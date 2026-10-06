import test from "node:test";
import assert from "node:assert/strict";
import {runFlowGraphCopy} from "../../wasm/crossing_assets/gpu-graph-copy.mjs";

globalThis.GPUBufferUsage = {STORAGE:1,COPY_DST:2,COPY_SRC:4,MAP_READ:8};
globalThis.GPUMapMode = {READ:1};

const reflection = JSON.stringify({
    kernel:"copy_f32",entryPoint:"copy_f32",workgroupSize:64,
    paramsBinding:null,params:[],paramsBytes:0,
    buffers:[
        {name:"source",binding:0,access:"read"},
        {name:"target",binding:1,access:"write"}
    ]
});
const wgsl = "@group(0) @binding(0) var<storage, read> source: array<f32>;\n"+
    "@group(0) @binding(1) var<storage, read_write> target: array<f32>;\n"+
    "@compute @workgroup_size(64) fn copy_f32(@builtin(global_invocation_id) gid:vec3<u32>) {\n"+
    "if (gid.x < 5u) { target[gid.x] = source[gid.x]; } }";

function fakeDevice({corrupt=false,compileError=false}={}) {
    const stats={groups:[],resources:[],submissions:0,compiled:0};
    function createBuffer({size}) {
        const b={
            bytes:new Uint8Array(size),destroyed:false,
            async mapAsync(mode){assert.equal(mode,GPUMapMode.READ);},
            getMappedRange(){return this.bytes.buffer;},
            unmap(){},
            destroy(){this.destroyed=true;}
        };
        stats.resources.push(b);
        return b;
    }
    const device={
        limits:{
            maxBufferSize:1<<20,
            maxStorageBufferBindingSize:1<<20,
            maxComputeWorkgroupsPerDimension:1024
        },
        createShaderModule({code}){
            assert.ok(code.includes("@compute"));
            stats.compiled++;
            return {async getCompilationInfo(){return {messages:compileError
                ? [{type:"error",lineNum:1,message:"bad WGSL"}]:[]};}};
        },
        createBuffer,
        createComputePipeline({compute}){
            assert.equal(compute.entryPoint,"copy_f32");
            return {getBindGroupLayout(){return {};}};
        },
        createBindGroup({entries}){return {entries};},
        createCommandEncoder(){
            const ops=[];
            return {
                beginComputePass(){
                    let group=null;
                    return {
                        setPipeline(){},
                        setBindGroup(_,binding){group=binding;},
                        dispatchWorkgroups(n){ops.push({type:"dispatch",n,group});},
                        end(){}
                    };
                },
                copyBufferToBuffer(src,srcOff,dst,dstOff,n){
                    ops.push({type:"blit",src,srcOff,dst,dstOff,n});
                },
                finish(){return ops;}
            };
        },
        queue:{
            writeBuffer(buf,off,src){
                const bytes=src instanceof ArrayBuffer
                    ? new Uint8Array(src)
                    : new Uint8Array(src.buffer,src.byteOffset,src.byteLength);
                buf.bytes.set(bytes,off);
            },
            submit(commandBuffers){
                stats.submissions++;
                for(const op of commandBuffers[0]){
                    if(op.type==="dispatch"){
                        stats.groups.push(op.n);
                        const entries=op.group.entries;
                        const input=entries.find(x=>x.binding===0).resource.buffer;
                        const output=entries.find(x=>x.binding===1).resource.buffer;
                        output.bytes.set(input.bytes);
                        if(corrupt)output.bytes[0]^=1;
                    } else {
                        op.dst.bytes.set(op.src.bytes.subarray(
                            op.srcOff,op.srcOff+op.n),op.dstOff);
                    }
                }
            },
            async onSubmittedWorkDone(){}
        }
    };
    return {device,stats};
}

test("Flow-generated graph reflection dispatches on WebGPU host with exact readback",async()=>{
    const {device,stats}=fakeDevice();
    const input=new Float32Array([1,-4,Math.PI,0.125,17]);
    const result=await runFlowGraphCopy(device,{reflection,wgsl,input});
    assert.equal(result.execution,"webgpu-device");
    assert.equal(result.elements,5);
    assert.deepEqual([...result.output],[...input]);
    assert.deepEqual(stats.groups,[1]);
    assert.equal(stats.submissions,1);
    assert.ok(stats.resources.every(x=>x.destroyed));
});

test("malformed graph reflection and over-limit inputs fail before GPU allocations",async()=>{
    const {device,stats}=fakeDevice();
    await assert.rejects(runFlowGraphCopy(device,{
        reflection:reflection.replace('"name":"source"','"name":"x;inject"'),
        wgsl,input:new Float32Array(5)
    }),/incompatible/);
    device.limits.maxStorageBufferBindingSize=8;
    await assert.rejects(runFlowGraphCopy(device,{
        reflection,wgsl,input:new Float32Array(5)
    }),/resource or dispatch limits/);
    assert.equal(stats.resources.length,0);
    assert.equal(stats.compiled,0);
});

test("shader compilation failure and corrupted GPU readback are never accepted",async()=>{
    const compile=fakeDevice({compileError:true});
    await assert.rejects(runFlowGraphCopy(compile.device,{
        reflection,wgsl,input:new Float32Array(5)
    }),/WGSL compile error/);
    assert.equal(compile.stats.resources.length,0);

    const broken=fakeDevice({corrupt:true});
    await assert.rejects(runFlowGraphCopy(broken.device,{
        reflection,wgsl,input:new Float32Array([1,2,3,4,5])
    }),/copy mismatch at element 0/);
    assert.ok(broken.stats.resources.every(x=>x.destroyed));
});
