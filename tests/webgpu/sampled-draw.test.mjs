// Browser host contract tested without GPU hardware.
// node --test tests/webgpu/sampled-draw.test.mjs
import test from "node:test";
import assert from "node:assert/strict";
import {renderFlowSampledDraw} from "../../wasm/crossing_assets/gpu-sampled-draw.mjs";

globalThis.GPUBufferUsage = {STORAGE:1,COPY_DST:2,INDEX:4,MAP_READ:8};
globalThis.GPUTextureUsage = {TEXTURE_BINDING:1,COPY_DST:2,RENDER_ATTACHMENT:4,COPY_SRC:8};
globalThis.GPUMapMode = {READ:1};

function fakeWebgpu({errors=[]}={}) {
    const stats = {draws:[],created:[],submissions:0,sourceWrites:0};
    function buffer(desc) {
        const value = {
            bytes:new Uint8Array(desc.size),destroyed:false,
            async mapAsync(mode) {assert.equal(mode,GPUMapMode.READ);},
            getMappedRange() {return this.bytes.buffer;},
            unmap() {},destroy(){this.destroyed=true;}
        };
        stats.created.push(value);
        return value;
    }
    function texture(desc) {
        const value = {
            desc,destroyed:false,
            createView(view={}) {return {texture:value,view};},
            destroy() {this.destroyed=true;}
        };
        stats.created.push(value);
        return value;
    }
    const device={
        limits:{maxTextureDimension2D:1024},
        createShaderModule({code}) {
            assert.ok(code.length>0);
            return {async getCompilationInfo(){return {messages:errors};}};
        },
        createBuffer:buffer,
        createTexture:texture,
        createSampler(desc){return {desc};},
        createRenderPipeline(desc){
            return {desc,getBindGroupLayout(index){return {index};}};
        },
        createBindGroup({entries}){return {entries};},
        createCommandEncoder(){
            const ops=[];
            return {
                beginRenderPass(desc){
                    const run={desc,indexed:false};
                    return {
                        setPipeline(p) {run.pipeline=p;},
                        setBindGroup(i,g){assert.equal(i,0);run.group=g;},
                        setIndexBuffer(b,format){run.indexBuffer=b;run.indexFormat=format;},
                        draw(n,instances,first,firstInstance){
                            run.draw={n,instances,first,firstInstance};
                        },
                        drawIndexed(n,instances,first,base,firstInstance){
                            run.indexed=true;
                            run.draw={n,instances,first,base,firstInstance};
                        },
                        end(){ops.push({type:"draw",data:run});}
                    };
                },
                copyTextureToBuffer(src,dst,size) {
                    ops.push({type:"copy",src,dst,size});
                },
                finish(){return ops.slice();}
            };
        },
        queue:{
            writeBuffer(buffer,offset,source) {
                const bytes=new Uint8Array(source.buffer,source.byteOffset,source.byteLength);
                buffer.bytes.set(bytes,offset);
            },
            writeTexture(){stats.sourceWrites++;},
            submit(batches){
                stats.submissions++;
                for(const op of batches[0]) {
                    if(op.type==="draw"){stats.draws.push(op.data);continue;}
                    const stride=op.dst.bytesPerRow;
                    const out=op.dst.buffer.bytes;
                    for(let y=0;y<op.size.height;y++) {
                        out.fill(0,y*stride,y*stride+op.size.width*4);
                        for(let x=0;x<op.size.width;x++) {
                            out.set([x*17,y*31,255,255],y*stride+x*4);
                        }
                    }
                }
            },
            async onSubmittedWorkDone(){}
        }
    };
    return {device,stats};
}

function descriptor(overrides={}) {
    const positions = new Float32Array([
        -1,-1,0,1, 1,-1,0,1, 0,1,0,1
    ]);
    return {
        width:3,height:2,textureWidth:2,textureHeight:2,
        textureRGBA:new Uint8Array(2*2*4).fill(255),
        positions,indices:new Uint16Array([0,1,2]),instances:3,
        wgsl:"@vertex fn scene_vs() {} @fragment fn scene_fs() {}",
        ...overrides
    };
}

test("draws indexed instances, submits, reads tightly packed pixels",async()=>{
    const {device,stats}=fakeWebgpu();
    const r=await renderFlowSampledDraw(device,descriptor({depth:true,samples:4}));
    assert.equal(r.execution,"webgpu-device");
    assert.equal(r.indexed,true);
    assert.equal(r.instances,3);
    assert.equal(r.rgba.length,3*2*4);
    assert.deepEqual([...r.rgba.slice(0,4)],[0,0,255,255]);
    assert.deepEqual([...r.rgba.slice(4,8)],[17,0,255,255]);
    assert.deepEqual([...r.rgba.slice(3*4,3*4+4)],[0,31,255,255]);
    assert.equal(stats.draws.length,1);
    assert.equal(stats.draws[0].indexed,true);
    assert.equal(stats.draws[0].draw.instances,3);
    assert.equal(stats.draws[0].indexFormat,"uint16");
    // Three u16 indices are six bytes. WebGPU requires an aligned 8-byte
    // GPUBuffer and 4-byte-aligned queue.writeBuffer upload.
    const bytes=stats.draws[0].indexBuffer.bytes;
    assert.equal(bytes.length,8);
    assert.deepEqual([...bytes.slice(0,6)],
        [...new Uint8Array(new Uint16Array([0,1,2]).buffer)]);
    assert.deepEqual([...bytes.slice(6)],[0,0]);
    assert.equal(stats.sourceWrites,1);
    assert.equal(stats.submissions,1);
    assert.ok(stats.created.every(x=>x.destroyed));
});

test("invalid index bounds rejected before allocating a GPU resource",async()=>{
    const {device,stats}=fakeWebgpu();
    await assert.rejects(renderFlowSampledDraw(device,
        descriptor({indices:new Uint16Array([0,1,7])})),/outside the position/);
    assert.equal(stats.created.length,0);
});

test("multisample and texture input validation fail closed",async()=>{
    const {device}=fakeWebgpu();
    await assert.rejects(renderFlowSampledDraw(device,
        descriptor({samples:8})),/MSAA/);
    await assert.rejects(renderFlowSampledDraw(device,
        descriptor({textureRGBA:new Uint8Array(15)})),/rgba8unorm/);
});

test("WebGPU buffer and readback limits fail before allocating resources",async()=>{
    const {device,stats}=fakeWebgpu();
    device.limits.maxBufferSize=256;
    await assert.rejects(renderFlowSampledDraw(device,
        descriptor({width:65,height:1})),/buffer capacity/);
    assert.equal(stats.created.length,0);
    device.limits.maxBufferSize=100000;
    device.limits.maxStorageBufferBindingSize=32;
    await assert.rejects(renderFlowSampledDraw(device,
        descriptor()),/buffer capacity/);
    assert.equal(stats.created.length,0);
});

test("shader compilation failure refuses draw and destroys resources",async()=>{
    const {device,stats}=fakeWebgpu({errors:[{
        type:"error",lineNum:7,message:"bad varying"
    }]});
    await assert.rejects(renderFlowSampledDraw(device,descriptor()),
        /WGSL compile failed/);
    assert.equal(stats.submissions,0);
    assert.ok(stats.created.every(x=>x.destroyed));
});

test("cube input uploads six layers and runs a real render pipeline",async()=>{
    const {device,stats}=fakeWebgpu();
    const r=await renderFlowSampledDraw(device,descriptor({
        cube:true, textureRGBA:new Uint8Array(2*2*6*4).fill(1),
        indices:undefined,instances:1
    }));
    assert.equal(r.indexed,false);
    assert.equal(stats.sourceWrites,6);
    assert.equal(stats.draws[0].draw.instances,1);
});
