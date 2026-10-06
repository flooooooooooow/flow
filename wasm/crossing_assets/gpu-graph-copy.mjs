// Execute Flow's GPU_GRAPH_OP_COPY_F32 on an actual WebGPU compute device.
// WGSL and the reflection JSON both come from gpu_graph.flow, not a
// separately handwritten inference/compute shader (#812).
import {runKernel} from "./webgpu-host.js";

function parseCopyContract(reflection, input, device) {
    const kernel = typeof reflection === "string"
        ? JSON.parse(reflection) : reflection;
    if (!kernel || !Array.isArray(kernel.buffers) ||
        kernel.buffers.length !== 2 || !Array.isArray(kernel.params) ||
        kernel.params.length !== 0 || kernel.paramsBinding !== null) {
        throw new TypeError("expected a two-buffer, parameter-free Flow copy kernel");
    }
    const src = kernel.buffers[0], dst = kernel.buffers[1];
    const ident = /^[A-Za-z_][A-Za-z0-9_]*$/;
    if (!src || !dst ||
        !ident.test(kernel.entryPoint) || kernel.entryPoint !== kernel.kernel ||
        !ident.test(src.name) || !ident.test(dst.name) ||
        src.name === dst.name || src.binding !== 0 ||
        dst.binding !== 1 || src.access !== "read" ||
        dst.access !== "write" ||
        !Number.isSafeInteger(kernel.workgroupSize) ||
        kernel.workgroupSize <= 0 || kernel.workgroupSize > 256) {
        throw new TypeError("incompatible Flow GPU copy reflection");
    }
    if (!(input instanceof Float32Array) || input.length === 0 ||
        !Number.isSafeInteger(input.length)) {
        throw new TypeError("copy input must be a nonempty Float32Array");
    }
    const maxBinding = device?.limits?.maxStorageBufferBindingSize ?? 134217728;
    const maxBuffer = device?.limits?.maxBufferSize ?? 268435456;
    const maxGroups = device?.limits?.maxComputeWorkgroupsPerDimension ?? 65535;
    if (input.byteLength > maxBinding || input.byteLength > maxBuffer ||
        Math.ceil(input.length/kernel.workgroupSize) > maxGroups) {
        throw new RangeError("Flow copy exceeds WebGPU resource or dispatch limits");
    }
    return {kernel,src,dst};
}

export async function runFlowGraphCopy(device, {wgsl, reflection, input}) {
    if (!device || typeof device.createComputePipeline !== "function") {
        throw new TypeError("a live WebGPU compute device is required");
    }
    if (typeof wgsl !== "string" || !wgsl.trim()) {
        throw new TypeError("Flow-generated WGSL source is required");
    }
    const {kernel,src,dst} = parseCopyContract(reflection,input,device);
    const {outputs,ms} = await runKernel(device,kernel,wgsl,
        {[src.name]:input},{},input.length);
    const output = outputs[dst.name];
    if (!(output instanceof Float32Array) ||
        output.length !== input.length) {
        throw new Error("Flow GPU copy did not return a complete readback");
    }
    // A copy should preserve the exact f32 bit patterns, not just an
    // approximate sum or a compiler success status.
    const expected = new Uint32Array(input.buffer,
        input.byteOffset,input.length);
    const actual = new Uint32Array(output.buffer,
        output.byteOffset,output.length);
    for (let i=0;i<expected.length;i++) {
        if (expected[i] !== actual[i]) {
            throw new Error("WebGPU copy mismatch at element "+i);
        }
    }
    return {output,ms,execution:"webgpu-device",elements:input.length};
}
