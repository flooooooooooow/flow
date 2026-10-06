// Node-only mocked device tests for the real WebGPU submission host.
// node --test tests/webgpu/kernel-chain.test.mjs
import test from "node:test";
import assert from "node:assert/strict";
import {runFlowKernelChain} from "../../wasm/crossing_assets/gpu-kernel-chain.mjs";

globalThis.GPUBufferUsage = {STORAGE:1, COPY_SRC:2, COPY_DST:4, UNIFORM:8, MAP_READ:16};
globalThis.GPUMapMode = {READ:1};

function fakeDevice({workgroupLimit=65535, shaderErrors=[]}={}) {
    const stats = {allocated:[], writes:0, submits:0, dispatched:[], bindGroups:[]};
    function makeBuffer(desc) {
        const b = {
            size:desc.size, bytes:new Uint8Array(desc.size), destroyed:false,
            async mapAsync(mode) {
                assert.equal(mode, GPUMapMode.READ);
                this.mapped = true;
            },
            getMappedRange() {
                assert.ok(this.mapped);
                return this.bytes.buffer;
            },
            unmap() {this.mapped=false;},
            destroy() {this.destroyed=true;}
        };
        stats.allocated.push(b);
        return b;
    }
    function f32(buf) {
        return new Float32Array(buf.bytes.buffer);
    }
    let ops=[];
    const device = {
        limits:{
            maxComputeWorkgroupsPerDimension:workgroupLimit,
            maxBufferSize:1048576,
            maxStorageBufferBindingSize:1048576
        },
        createBuffer:makeBuffer,
        createShaderModule({code,label}) {
            assert.equal(typeof code,"string");
            assert.ok(code.length>0);
            return {label,async getCompilationInfo(){return {messages:shaderErrors};}};
        },
        async createComputePipelineAsync(desc) {
            return {
                name:desc.compute.entryPoint,
                getBindGroupLayout(index) {assert.equal(index,0);return {index};}
            };
        },
        createBindGroup({layout,entries}) {
            assert.equal(layout.index,0);
            const sorted = entries.toSorted((a,b)=>a.binding-b.binding);
            stats.bindGroups.push(sorted);
            return {entries:sorted};
        },
        createCommandEncoder() {
            ops=[];
            return {
                beginComputePass() {
                    const pass={};
                    return {
                        setPipeline(pipeline){pass.pipeline=pipeline;},
                        setBindGroup(index,group){assert.equal(index,0);pass.group=group;},
                        dispatchWorkgroups(count) {pass.groups=count;},
                        end(){ops.push({type:"pass",...pass});}
                    };
                },
                copyBufferToBuffer(src,sourceOffset,dst,targetOffset,size) {
                    ops.push({type:"copy",src,sourceOffset,dst,targetOffset,size});
                },
                finish(){return ops.slice();}
            };
        },
        queue:{
            writeBuffer(buffer,offset,source) {
                stats.writes++;
                const a=source instanceof ArrayBuffer
                    ? new Uint8Array(source)
                    : new Uint8Array(source.buffer,source.byteOffset,source.byteLength);
                buffer.bytes.set(a,offset);
            },
            submit(batches) {
                stats.submits++;
                for (const op of batches[0]) {
                    if(op.type==="copy") {
                        op.dst.bytes.set(
                            op.src.bytes.slice(op.sourceOffset,op.sourceOffset+op.size),
                            op.targetOffset
                        );
                        continue;
                    }
                    stats.dispatched.push(op.pipeline.name);
                    const bindings=Object.fromEntries(op.group.entries.map(e=>[e.binding,e.resource.buffer]));
                    const input=f32(bindings[0]);
                    const output=f32(bindings[1]);
                    if (op.pipeline.name === "preprocess") {
                        for(let i=0;i<output.length;i++)output[i]=input[i]/255;
                    } else if (op.pipeline.name === "postprocess") {
                        for(let i=0;i<output.length;i++)output[i]=input[i]*2;
                    } else {
                        throw new Error("unknown mocked kernel");
                    }
                }
            },
            async onSubmittedWorkDone(){}
        }
    };
    return {device,stats};
}

function stage(entryPoint,input,output,n=4,workgroupSize=4) {
    return {
        descriptor:{
            entryPoint, workgroupSize,
            buffers:[
                {name:"x",binding:0,access:"read"},
                {name:"y",binding:1,access:"write"}
            ],
            params:[], paramsBinding:null
        },
        wgsl:"@compute @workgroup_size(4) fn "+entryPoint+"() {}",
        bindings:{x:input,y:output},
        count:n
    };
}

test("two Flow shader stages execute on reused GPU buffers, one final readback",async()=>{
    const {device,stats}=fakeDevice();
    const result=await runFlowKernelChain(device,{
        resources:{
            input:{length:4,initial:new Float32Array([255,127.5,0,63.75])},
            intermediate:{length:4}, output:{length:4}
        },
        stages:[stage("preprocess","input","intermediate"),
                stage("postprocess","intermediate","output")],
        readback:["output"]
    });
    assert.equal(result.execution,"webgpu-device");
    assert.equal(result.stageCount,2);
    assert.equal(result.resourceCount,3);
    assert.deepEqual(stats.dispatched,["preprocess","postprocess"]);
    assert.equal(stats.submits,1);
    assert.equal(stats.writes,1,"intermediate GPU buffers should never roundtrip");
    assert.deepEqual([...result.outputs.output],[2,1,0,0.5]);
    assert.equal(stats.allocated.length,4);
    assert.ok(stats.allocated.every(b=>b.destroyed),"all temporary buffers cleaned");
    assert.equal(stats.bindGroups[0][1].resource.buffer,
                 stats.bindGroups[1][0].resource.buffer,
                 "the intermediate must retain physical buffer identity");
});

test("invalid dispatch fails before submission and cleans allocations",async()=>{
    const {device,stats}=fakeDevice({workgroupLimit:1});
    await assert.rejects(runFlowKernelChain(device,{
        resources:{input:{length:8},output:{length:8}},
        stages:[stage("preprocess","input","output",8,4)],
        readback:["output"]
    }), /maxComputeWorkgroupsPerDimension/);
    assert.equal(stats.submits,0);
    assert.ok(stats.allocated.every(b=>b.destroyed));
});

test("two arguments cannot alias same physical GPU buffer in a pass",async()=>{
    const {device}=fakeDevice();
    await assert.rejects(runFlowKernelChain(device,{
        resources:{data:{length:4}},
        stages:[stage("preprocess","data","data")],
        readback:["data"]
    }), /same GPU resource/);
});

test("Flow shader compilation errors are never interpreted as success",async()=>{
    const {device,stats}=fakeDevice({
        shaderErrors:[{type:"error",lineNum:1,message:"bad compute body"}]
    });
    await assert.rejects(runFlowKernelChain(device,{
        resources:{input:{length:4},output:{length:4}},
        stages:[stage("preprocess","input","output")],
        readback:["output"]
    }), /WGSL compile failed/);
    assert.equal(stats.submits,0);
    assert.ok(stats.allocated.every(b=>b.destroyed));
});

test("host rejects incorrectly shaped input buffers",async()=>{
    const {device}=fakeDevice();
    await assert.rejects(runFlowKernelChain(device,{
        resources:{input:{length:4,initial:new Float32Array(3)},output:{length:4}},
        stages:[stage("preprocess","input","output")],readback:["output"]
    }), /Float32Array length/);
});
