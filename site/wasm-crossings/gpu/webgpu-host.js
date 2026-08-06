// Generic WebGPU host for Flow @gpu kernels.
//
// It reads FLOW_KERNELS, the reflection that src/flow/wgsl_codegen.py emits
// alongside each .wgsl: binding indices, storage access modes, the scalar
// layout of the uniform block, and the workgroup size. Nothing here knows
// anything about vector add in particular, so a new @gpu kernel needs no new
// JavaScript.

export async function getDevice() {
    if (!navigator.gpu) throw new Error("navigator.gpu missing: this browser has no WebGPU");
    const adapter = await navigator.gpu.requestAdapter();
    if (!adapter) throw new Error("requestAdapter returned null: no WebGPU adapter available");
    const device = await adapter.requestDevice();
    return { adapter, device };
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
 * Run one kernel.
 *   inputs   {name: Float32Array} for every `read` storage binding
 *   scalars  {name: number} for every uniform parameter
 *   count    elements in each buffer, and the dispatch extent
 * Returns {outputs: {name: Float32Array}, ms}
 */
export async function runKernel(device, kernel, code, inputs, scalars, count) {
    const module = device.createShaderModule({ code, label: kernel.kernel });

    // Surface WGSL compile diagnostics rather than failing later and blaming
    // the dispatch.
    const info = await module.getCompilationInfo();
    const errors = info.messages.filter((m) => m.type === "error");
    if (errors.length) {
        throw new Error(
            "WGSL compile error in " + kernel.kernel + ": " +
            errors.map((m) => `line ${m.lineNum}: ${m.message}`).join("; ")
        );
    }

    const bytes = count * 4;
    const gpuBuffers = {};
    const entries = [];
    const readbackNames = [];

    for (const b of kernel.buffers) {
        if (b.access === "read") {
            const buffer = device.createBuffer({
                size: bytes,
                usage: GPUBufferUsage.STORAGE | GPUBufferUsage.COPY_DST,
                label: b.name,
            });
            device.queue.writeBuffer(buffer, 0, inputs[b.name]);
            gpuBuffers[b.name] = buffer;
        } else {
            gpuBuffers[b.name] = device.createBuffer({
                size: bytes,
                usage: GPUBufferUsage.STORAGE | GPUBufferUsage.COPY_SRC | GPUBufferUsage.COPY_DST,
                label: b.name,
            });
            readbackNames.push(b.name);
        }
        entries.push({ binding: b.binding, resource: { buffer: gpuBuffers[b.name] } });
    }

    let paramsBuffer = null;
    if (kernel.paramsBinding !== null && kernel.params.length) {
        paramsBuffer = device.createBuffer({
            size: kernel.paramsBytes,
            usage: GPUBufferUsage.UNIFORM | GPUBufferUsage.COPY_DST,
            label: "params",
        });
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

    const staging = {};
    for (const name of readbackNames) {
        staging[name] = device.createBuffer({
            size: bytes,
            usage: GPUBufferUsage.COPY_DST | GPUBufferUsage.MAP_READ,
        });
    }

    const t0 = performance.now();
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
    const ms = performance.now() - t0;

    const outputs = {};
    for (const name of readbackNames) {
        await staging[name].mapAsync(GPUMapMode.READ);
        outputs[name] = new Float32Array(staging[name].getMappedRange().slice(0));
        staging[name].unmap();
    }

    for (const b of Object.values(gpuBuffers)) b.destroy();
    for (const b of Object.values(staging)) b.destroy();
    if (paramsBuffer) paramsBuffer.destroy();

    return { outputs, ms };
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
