import test from "node:test";
import assert from "node:assert/strict";
import {runFlowGpuPasses} from "../../wasm/crossing_assets/gpu-multipass.mjs";

globalThis.GPUBufferUsage={
    STORAGE:1,COPY_DST:2,COPY_SRC:4,MAP_READ:8,UNIFORM:16
};
globalThis.GPUMapMode={READ:1};

const copyReflection={
    entryPoint:"copy",workgroupSize:64,
    buffers:[
        {name:"src",binding:0,access:"read"},
        {name:"dst",binding:1,access:"write"}
    ],params:[],paramsBinding:null,paramsBytes:0
};
const scaleReflection={
    entryPoint:"scale",workgroupSize:64,
    buffers:[
        {name:"x",binding:0,access:"read"},
        {name:"y",binding:1,access:"write"}
    ],
    params:[{name:"alpha",type:"f32"}],
    paramsBinding:2,paramsBytes:16
};
function plan(overrides={}){
    return {
        resources:{input:new Float32Array([1,2,3]),mid:3,result:3},
        passes:[
            {reflection:copyReflection,wgsl:"@compute fn copy() {}",
             bindings:{src:"input",dst:"mid"},dispatchElements:3},
            {reflection:scaleReflection,wgsl:"@compute fn scale() {}",
             bindings:{x:"mid",y:"result"},dispatchElements:3,
             scalars:{alpha:2}}
        ],
        readback:["result"],...overrides
    };
}

function fakeWebGpu({compileError=false,submissionError=false}={}){
    const stats={resources:[],copies:0,dispatched:[],submissions:0};
    function createBuffer({size}){
        const b={
            bytes:new Uint8Array(size),destroyed:false,
            async mapAsync(m){assert.equal(m,GPUMapMode.READ);},
            getMappedRange(){return this.bytes.buffer;},
            unmap(){},destroy(){this.destroyed=true;}
        };
        stats.resources.push(b);
        return b;
    }
    const device={
        limits:{maxBufferSize:65536,maxStorageBufferBindingSize:65536,
            maxComputeInvocationsPerWorkgroup:256,maxComputeWorkgroupSizeX:256,
            maxComputeWorkgroupsPerDimension:65535},
        createBuffer,
        createShaderModule({code}){
            assert.ok(code.includes("@compute"));
            return {async getCompilationInfo(){
                return {messages:compileError?[{
                    type:"error",lineNum:1,message:"bad shader"
                }]:[]};
            }};
        },
        createComputePipeline({compute}){
            return {entry:compute.entryPoint,getBindGroupLayout(){return {};}};
        },
        createBindGroup({entries}){return {entries};},
        createCommandEncoder(){
            const commands=[];
            return {
                beginComputePass(){
                    let pipeline=null,group=null,groups=0;
                    return {
                        setPipeline(p){pipeline=p;},
                        setBindGroup(_,g){group=g;},
                        dispatchWorkgroups(n){groups=n;},
                        end(){commands.push({type:"compute",pipeline,group,groups});}
                    };
                },
                copyBufferToBuffer(src,srcOffset,dst,dstOffset,n){
                    commands.push({type:"copy",src,srcOffset,dst,dstOffset,n});
                },
                finish(){return commands;}
            };
        },
        queue:{
            writeBuffer(buffer,offset,data){
                const bytes=data instanceof ArrayBuffer
                    ? new Uint8Array(data)
                    : new Uint8Array(data.buffer,data.byteOffset,data.byteLength);
                buffer.bytes.set(bytes,offset);
            },
            submit(commands){
                if(submissionError)throw Error("GPU queue failure");
                stats.submissions++;
                for(const cmd of commands[0]){
                    if(cmd.type==="copy"){
                        stats.copies++;
                        cmd.dst.bytes.set(cmd.src.bytes.subarray(
                            cmd.srcOffset,cmd.srcOffset+cmd.n),cmd.dstOffset);
                        continue;
                    }
                    stats.dispatched.push([cmd.pipeline.entry,cmd.groups]);
                    const binding=n=>cmd.group.entries
                        .find(e=>e.binding===n).resource.buffer;
                    const input=new Float32Array(binding(0).bytes.buffer);
                    const output=new Float32Array(binding(1).bytes.buffer);
                    if(cmd.pipeline.entry==="copy"){
                        output.set(input);
                    } else if(cmd.pipeline.entry==="scale"){
                        const alpha=new DataView(binding(2).bytes.buffer)
                            .getFloat32(0,true);
                        for(let i=0;i<output.length;i++){
                            output[i]=input[i]*alpha;
                        }
                    } else throw Error("unknown mock kernel");
                }
            },
            async onSubmittedWorkDone(){}
        }
    };
    return {device,stats};
}

test("two Flow GPU kernels share device buffers, one submit and final readback",async()=>{
    const {device,stats}=fakeWebGpu();
    const result=await runFlowGpuPasses(device,plan());
    assert.equal(result.execution,"webgpu-device");
    assert.equal(result.passes,2);
    assert.equal(result.intermediateCpuCopies,0);
    assert.deepEqual([...result.outputs.result],[2,4,6]);
    assert.deepEqual(stats.dispatched,[["copy",1],["scale",1]]);
    assert.equal(stats.submissions,1);
    assert.equal(stats.copies,1);
    assert.ok(stats.resources.every(x=>x.destroyed));
});

test("rejects uninitialised tensor, shape overflow and same-pass alias before GPU work",async()=>{
    const {device,stats}=fakeWebGpu();
    await assert.rejects(runFlowGpuPasses(device,plan({
        resources:{input:3,mid:3,result:3}
    })),/read before write/);
    const oversized=plan();
    oversized.passes[0].requiredElements={src:4,dst:3};
    await assert.rejects(runFlowGpuPasses(device,oversized),/shape exceeds/);
    const alias=plan();
    alias.passes[0].bindings={src:"input",dst:"input"};
    await assert.rejects(runFlowGpuPasses(device,alias),/same-pass/);
    assert.equal(stats.resources.length,0);
});

test("no GPU result is claimed when a stage fails; buffers are destroyed",async()=>{
    const badShader=fakeWebGpu({compileError:true});
    await assert.rejects(runFlowGpuPasses(badShader.device,plan()),
        /WGSL compilation failed/);
    assert.equal(badShader.stats.submissions,0);
    assert.ok(badShader.stats.resources.every(x=>x.destroyed));
    const badQueue=fakeWebGpu({submissionError:true});
    await assert.rejects(runFlowGpuPasses(badQueue.device,plan()),
        /GPU queue failure/);
    assert.ok(badQueue.stats.resources.every(x=>x.destroyed));
});
