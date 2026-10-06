// Persistent WebGPU resources for a chain of Flow-generated @gpu kernels.
// Kernel descriptors and WGSL must come from Flow's GPU reflection/emitter;
// this host does not synthesize or embed a second shader language.
//
// Example shape:
//   runFlowKernelChain(device, {
//     resources: {raw:{length:784,initial:new Float32Array(784)},
//                 norm:{length:784}, weights:{length:784*16},
//                 result:{length:16}},
//     stages: [{ descriptor: flowKernel, wgsl: flowWgsl,
//                bindings:{raw:"raw",norm:"norm"}, scalars:{n:784}, count:784 }],
//     readback: ["result"]
//   });
//
// Intermediates never leave GPU storage. The optional readback is explicit.
// This is a compute executor, NOT an adapter for render/texture passes.

function positiveInteger(n, label) {
    if (!Number.isSafeInteger(n) || n <= 0) {
        throw new RangeError(label + " must be a positive safe integer");
    }
    return n;
}

function maxLimit(device, key, fallback) {
    const value = device?.limits?.[key];
    return Number.isSafeInteger(value) && value > 0 ? value : fallback;
}

function reflectParams(descriptor, scalars) {
    const params = descriptor.params || [];
    if (!params.length) return null;
    const size = positiveInteger(descriptor.paramsBytes, "paramsBytes");
    if (size % 16 !== 0) {
        throw new RangeError("Flow uniform paramsBytes must be 16-byte aligned");
    }
    const result = new ArrayBuffer(size);
    const view = new DataView(result);
    params.forEach((p, index) => {
        const offset = index * 4;
        if (offset + 4 > size) throw new RangeError("Flow parameter block too small");
        const value = scalars[p.name];
        if (value === undefined || !Number.isFinite(value)) {
            throw new TypeError("missing/invalid scalar " + p.name);
        }
        if (p.type === "f32") view.setFloat32(offset, value, true);
        else if (p.type === "u32") {
            if (!Number.isInteger(value) || value < 0 || value > 0xffffffff) {
                throw new RangeError("u32 parameter " + p.name + " out of range");
            }
            view.setUint32(offset, value, true);
        } else if (p.type === "i32") {
            if (!Number.isInteger(value) || value < -2147483648 || value > 2147483647) {
                throw new RangeError("i32 parameter " + p.name + " out of range");
            }
            view.setInt32(offset, value, true);
        } else {
            throw new TypeError("unsupported Flow scalar " + p.type);
        }
    });
    return result;
}

function reportShaderErrors(info, name) {
    const failures = info.messages.filter(message => message.type === "error");
    if (failures.length) {
        throw new Error("WGSL compile failed (" + name + "): " +
            failures.map(m => (m.lineNum || "?") + ": " + m.message).join("; "));
    }
}

function assertDescriptor(stage, index, gpuBuffers, resources, device) {
    const d = stage.descriptor;
    if (!d || typeof d.entryPoint !== "string" || !d.entryPoint) {
        throw new TypeError("stage " + index + ": no Flow kernel entryPoint");
    }
    const wg = positiveInteger(d.workgroupSize, "workgroupSize");
    const n = positiveInteger(stage.count, "dispatch element count");
    const dispatch = Math.ceil(n / wg);
    if (dispatch > maxLimit(device, "maxComputeWorkgroupsPerDimension", 65535)) {
        throw new RangeError("dispatch exceeds maxComputeWorkgroupsPerDimension");
    }
    if (!Array.isArray(d.buffers) || !d.buffers.length || !stage.bindings) {
        throw new TypeError("stage " + index + ": expected Flow buffer reflection");
    }
    const entries = [];
    const seenBindings = new Set();
    const seenResources = new Set();
    for (const binding of d.buffers) {
        const resourceId = stage.bindings[binding.name];
        if (typeof resourceId !== "string" || !gpuBuffers.has(resourceId)) {
            throw new TypeError("missing Flow binding " + binding.name + " at stage " + index);
        }
        if (!Number.isInteger(binding.binding) || binding.binding < 0 ||
            seenBindings.has(binding.binding)) {
            throw new TypeError("duplicate/invalid shader binding index");
        }
        if (seenResources.has(resourceId)) {
            throw new TypeError("same GPU resource bound to multiple shader slots");
        }
        if (!["read", "write", "read_write"].includes(binding.access)) {
            throw new TypeError("unknown Flow buffer access mode " + binding.access);
        }
        const record = resources[resourceId];
        if (record.length < n && !stage.allowNonlinear) {
            throw new RangeError("stage accesses more elements than " + resourceId);
        }
        if (record.length * 4 > maxLimit(device, "maxStorageBufferBindingSize", Number.MAX_SAFE_INTEGER)) {
            throw new RangeError("storage resource exceeds device binding limit");
        }
        seenBindings.add(binding.binding);
        seenResources.add(resourceId);
        entries.push({binding:binding.binding, resource:{buffer:gpuBuffers.get(resourceId)}});
    }
    return {entries, seenBindings, n, dispatch};
}

/**
 * Execute one or more Flow kernels using one persistent GPU buffer per resource.
 *
 * resources: name -> { length: positive element count, initial?: Float32Array }
 * stages: ordered [{descriptor: Flow reflection, wgsl: Flow-produced shader,
 *                    bindings:{kernelArgument:resourceName}, scalars, count}]
 * readback: array of resource names, explicit CPU boundary at graph end.
 *
 * No CPU transfers between stages. GPU device errors reject the whole run;
 * no fabricated parity verdict is emitted on failure.
 */
export async function runFlowKernelChain(device, {resources, stages, readback = []}) {
    if (!device || typeof device.createBuffer !== "function" ||
        !device.queue || typeof device.queue.submit !== "function") {
        throw new TypeError("a live WebGPU device is required");
    }
    if (!resources || typeof resources !== "object" ||
        !Array.isArray(stages) || !stages.length ||
        !Array.isArray(readback)) {
        throw new TypeError("resources, stages and readback must be provided");
    }

    const buffers = new Map();
    const owned = [];
    const staging = new Map();
    const usage = GPUBufferUsage.STORAGE | GPUBufferUsage.COPY_SRC | GPUBufferUsage.COPY_DST;
    const t0 = typeof performance === "object" ? performance.now() : Date.now();

    try {
        for (const [name, desc] of Object.entries(resources)) {
            const length = positiveInteger(desc?.length, "resource " + name + " length");
            if (length > Math.floor(Number.MAX_SAFE_INTEGER / 4)) {
                throw new RangeError("resource byte-size overflow");
            }
            const bytes = length * 4;
            if (bytes > maxLimit(device, "maxBufferSize", Number.MAX_SAFE_INTEGER)) {
                throw new RangeError("resource too large for WebGPU device");
            }
            if (desc.initial !== undefined &&
                (!(desc.initial instanceof Float32Array) || desc.initial.length !== length)) {
                throw new TypeError("resource " + name + " initial must match Float32Array length");
            }
            const buffer = device.createBuffer({size:bytes, usage, label:"Flow " + name});
            owned.push(buffer);
            buffers.set(name, buffer);
            if (desc.initial !== undefined) {
                device.queue.writeBuffer(buffer, 0, desc.initial);
            }
        }

        const encoder = device.createCommandEncoder();
        for (const [index, stage] of stages.entries()) {
            const {entries, seenBindings, dispatch} =
                assertDescriptor(stage, index, buffers, resources, device);
            if (typeof stage.wgsl !== "string" || !stage.wgsl) {
                throw new TypeError("missing Flow-produced WGSL for stage " + index);
            }
            const d = stage.descriptor;
            const module = device.createShaderModule({
                code:stage.wgsl, label:"Flow " + d.entryPoint
            });
            reportShaderErrors(await module.getCompilationInfo(), d.entryPoint);
            const pipeline = device.createComputePipelineAsync
                ? await device.createComputePipelineAsync({
                    layout:"auto", compute:{module,entryPoint:d.entryPoint}
                })
                : device.createComputePipeline({
                    layout:"auto", compute:{module,entryPoint:d.entryPoint}
                });

            const params = reflectParams(d, stage.scalars || {});
            if (params) {
                const binding = d.paramsBinding;
                if (!Number.isInteger(binding) || binding < 0 || seenBindings.has(binding)) {
                    throw new TypeError("invalid Flow uniform binding");
                }
                const ub = device.createBuffer({
                    size:params.byteLength,
                    usage:GPUBufferUsage.UNIFORM | GPUBufferUsage.COPY_DST,
                    label:"Flow " + d.entryPoint + " uniforms"
                });
                owned.push(ub);
                device.queue.writeBuffer(ub, 0, params);
                entries.push({binding,resource:{buffer:ub}});
            }

            const group = device.createBindGroup({
                layout:pipeline.getBindGroupLayout(0), entries
            });
            const pass = encoder.beginComputePass();
            pass.setPipeline(pipeline);
            pass.setBindGroup(0, group);
            pass.dispatchWorkgroups(dispatch);
            pass.end();
        }

        for (const name of readback) {
            if (!buffers.has(name) || staging.has(name)) {
                throw new TypeError("readback resource unknown/duplicated: " + name);
            }
            const bytes = resources[name].length * 4;
            const rb = device.createBuffer({
                size:bytes, usage:GPUBufferUsage.COPY_DST | GPUBufferUsage.MAP_READ,
                label:"Flow readback " + name
            });
            owned.push(rb);
            staging.set(name, rb);
            encoder.copyBufferToBuffer(buffers.get(name), 0, rb, 0, bytes);
        }

        device.queue.submit([encoder.finish()]);
        await device.queue.onSubmittedWorkDone();

        const outputs = {};
        for (const [name, rb] of staging) {
            await rb.mapAsync(GPUMapMode.READ);
            outputs[name] = new Float32Array(rb.getMappedRange().slice(0));
            rb.unmap();
        }
        return {
            outputs,
            stageCount:stages.length,
            resourceCount:buffers.size,
            elapsedMs:(typeof performance === "object" ? performance.now() : Date.now()) - t0,
            execution:"webgpu-device"
        };
    } finally {
        for (const buffer of owned) buffer.destroy();
    }
}
