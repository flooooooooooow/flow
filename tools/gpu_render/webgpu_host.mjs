// WebGPU host for Flow render jobs (#811).
//
// A Flow program built with lib/stdlib/gpu_render.flow writes a job
// directory: job.txt (one command per line), the WGSL and Metal shaders
// that flowc-compiled Flow code emitted, and raw buffer and texture blobs.
// This host replays the job on a real WebGPU device and writes the output
// texture as tightly packed rgba8 bytes. runtime/gpu_render_metal.m replays
// the same job on Metal. Neither host contains shader source of its own.
//
//   deno run --allow-read --allow-write tools/gpu_render/webgpu_host.mjs JOBDIR OUT.rgba
//
// Exit codes: 0 rendered, 1 job or device error, 3 no WebGPU adapter.

const FORMATS = { rgba8: "rgba8unorm", rgba16f: "rgba16float", depth32f: "depth32float" };
const USE_SAMPLED = 1, USE_STORAGE = 2, USE_COLOR = 4, USE_DEPTH = 8;

function fail(msg) {
    console.error("webgpu_host: " + msg);
    Deno.exit(1);
}

function parseJob(text) {
    const lines = text.split("\n").map(l => l.trim()).filter(l => l && !l.startsWith("#"));
    if (!lines.length || lines[0] !== "flowjob 1") fail("not a flowjob 1 file");
    return lines.slice(1).map(l => l.split(/\s+/));
}

function int(tok, what) {
    const n = Number(tok);
    if (!Number.isInteger(n)) fail("bad integer for " + what + ": " + tok);
    return n;
}

async function checkShader(module, label) {
    const info = await module.getCompilationInfo();
    const errs = info.messages.filter(m => m.type === "error");
    if (errs.length) {
        fail("WGSL compile failed (" + label + "): " +
            errs.map(m => m.lineNum + ":" + m.linePos + " " + m.message).join("; "));
    }
}

async function main() {
    const [dir, outPath] = Deno.args;
    if (!dir || !outPath) fail("usage: webgpu_host.mjs JOBDIR OUT.rgba");
    if (!globalThis.navigator?.gpu) {
        console.error("webgpu_host: navigator.gpu is not available");
        Deno.exit(3);
    }
    const adapter = await navigator.gpu.requestAdapter();
    if (!adapter) {
        console.error("webgpu_host: no WebGPU adapter");
        Deno.exit(3);
    }
    const device = await adapter.requestDevice();
    device.pushErrorScope("validation");

    const cmds = parseJob(await Deno.readTextFile(dir + "/job.txt"));
    const read = async name => await Deno.readFile(dir + "/" + name);

    let width = 0, height = 0;
    const buffers = new Map(), textures = new Map(), samplers = new Map();
    const shaders = new Map(), pipes = new Map(), groups = new Map();
    const passes = [];
    let output = -1;
    let bundling = false;

    for (const c of cmds) {
        const op = c[0];
        if (op === "size") {
            width = int(c[1], "width");
            height = int(c[2], "height");
        } else if (op === "buffer") {
            const data = await read(c[2]);
            if (data.length !== int(c[3], "buffer bytes")) fail("buffer " + c[1] + " size mismatch");
            const usageName = c[4];
            let usage = GPUBufferUsage.COPY_DST;
            if (usageName === "vertex") usage |= GPUBufferUsage.VERTEX;
            else if (usageName === "index") usage |= GPUBufferUsage.INDEX;
            else if (usageName === "uniform") usage |= GPUBufferUsage.UNIFORM;
            else fail("unknown buffer usage " + usageName);
            const size = Math.max(16, (data.length + 3) & ~3);
            const buf = device.createBuffer({ size, usage, mappedAtCreation: true });
            new Uint8Array(buf.getMappedRange()).set(data);
            buf.unmap();
            buffers.set(c[1], { buf, bytes: data.length });
        } else if (op === "texture") {
            const [, id, dim, fmt, w, h, layers, samples, usageBits, file] = c;
            const format = FORMATS[fmt];
            if (!format) fail("unknown texture format " + fmt);
            const bits = int(usageBits, "usage");
            let usage = GPUTextureUsage.COPY_SRC | GPUTextureUsage.COPY_DST;
            if (bits & USE_SAMPLED) usage |= GPUTextureUsage.TEXTURE_BINDING;
            if (bits & USE_STORAGE) usage |= GPUTextureUsage.STORAGE_BINDING;
            if (bits & (USE_COLOR | USE_DEPTH)) usage |= GPUTextureUsage.RENDER_ATTACHMENT;
            const sampleCount = int(samples, "samples");
            if (sampleCount > 1) usage &= ~(GPUTextureUsage.COPY_SRC | GPUTextureUsage.COPY_DST);
            if (fmt === "depth32f") usage &= ~GPUTextureUsage.COPY_DST;
            const tex = device.createTexture({
                size: [int(w, "w"), int(h, "h"), int(layers, "layers")],
                format, usage, sampleCount,
            });
            if (file !== "-") {
                const data = await read(file);
                const bpp = fmt === "rgba16f" ? 8 : 4;
                device.queue.writeTexture({ texture: tex }, data,
                    { bytesPerRow: int(w, "w") * bpp, rowsPerImage: int(h, "h") },
                    [int(w, "w"), int(h, "h"), int(layers, "layers")]);
            }
            textures.set(id, { tex, dim, fmt, w: int(w, "w"), h: int(h, "h") });
        } else if (op === "sampler") {
            const [, id, minf, magf, au, av, aw] = c;
            const addr = a => a === "repeat" ? "repeat" : "clamp-to-edge";
            samplers.set(id, device.createSampler({
                minFilter: minf, magFilter: magf, mipmapFilter: "nearest",
                addressModeU: addr(au), addressModeV: addr(av), addressModeW: addr(aw),
            }));
        } else if (op === "shader") {
            const code = await Deno.readTextFile(dir + "/" + c[2]);
            const module = device.createShaderModule({ code, label: c[2] });
            await checkShader(module, c[2]);
            shaders.set(c[1], module);
        } else if (op === "pipeline") {
            const [, id, shader, topology, cull, depth, blend, samples, colorFmt, hasDepth] = c;
            pipes.set(id, {
                shader, topology, cull, depth, blend,
                samples: int(samples, "samples"), colorFmt, hasDepth: hasDepth === "1",
                vbufs: [], binds: [], gpu: null,
            });
        } else if (op === "vbuf") {
            const p = pipes.get(c[1]);
            p.vbufs[int(c[2], "slot")] = {
                arrayStride: int(c[3], "stride"), stepMode: c[4], attributes: [],
            };
        } else if (op === "vattr") {
            const p = pipes.get(c[1]);
            const n = int(c[4].slice(4), "components");
            p.vbufs[int(c[2], "slot")].attributes.push({
                shaderLocation: int(c[3], "location"),
                format: n === 1 ? "float32" : "float32x" + n,
                offset: int(c[5], "offset"),
            });
        } else if (op === "pbind") {
            pipes.get(c[1]).binds.push(c.slice(2));
        } else if (op === "group") {
            groups.set(c[1], { pipe: c[2], uniform: c[3], tex: [], gpu: null });
        } else if (op === "gtex") {
            groups.get(c[1]).tex.push({ slot: int(c[2], "slot"), tex: c[3], smp: c[4] });
        } else if (op === "pass") {
            const [, color, resolve, depth, load, r, g, b, a, dclear] = c;
            passes.push({
                color, resolve, depth, load,
                clear: [Number(r), Number(g), Number(b), Number(a)],
                depthClear: Number(dclear), items: [],
            });
        } else if (op === "bundle-begin") {
            bundling = true;
            passes.at(-1).items.push({ bundle: [] });
        } else if (op === "bundle-end") {
            bundling = false;
        } else if (op === "draw") {
            const [, pipe, group, ibuf, ifmt, count, instances, first, baseVertex, firstInstance, ...vbs] = c;
            const d = {
                pipe, group, ibuf, ifmt,
                count: int(count, "count"), instances: int(instances, "instances"),
                first: int(first, "first"), baseVertex: int(baseVertex, "base vertex"),
                firstInstance: int(firstInstance, "first instance"), vbs,
            };
            const pass = passes.at(-1);
            if (!pass) fail("draw before pass");
            if (bundling) pass.items.at(-1).bundle.push(d);
            else pass.items.push(d);
        } else if (op === "output") {
            output = c[1];
        } else {
            fail("unknown command " + op);
        }
    }

    function layoutFor(p) {
        const entries = [];
        for (const b of p.binds) {
            const vis = int(b[b.length - 1], "stages");
            let visibility = 0;
            if (vis & 1) visibility |= GPUShaderStage.VERTEX;
            if (vis & 2) visibility |= GPUShaderStage.FRAGMENT;
            if (b[0] === "uniform") {
                entries.push({ binding: 0, visibility, buffer: { type: "uniform" } });
            } else if (b[0] === "tex") {
                const slot = int(b[1], "slot");
                entries.push({ binding: 1 + 2 * slot, visibility,
                    texture: { sampleType: "float", viewDimension: b[2] === "cube" ? "cube" : "2d" } });
                entries.push({ binding: 2 + 2 * slot, visibility, sampler: { type: "filtering" } });
            }
        }
        return device.createBindGroupLayout({ entries });
    }

    function pipelineFor(id) {
        const p = pipes.get(id);
        if (!p) fail("unknown pipeline " + id);
        if (p.gpu) return p;
        const module = shaders.get(p.shader);
        p.layout = layoutFor(p);
        const blend = p.blend === "alpha"
            ? { color: { srcFactor: "src-alpha", dstFactor: "one-minus-src-alpha" },
                alpha: { srcFactor: "one", dstFactor: "one-minus-src-alpha" } }
            : p.blend === "add"
                ? { color: { srcFactor: "one", dstFactor: "one" },
                    alpha: { srcFactor: "one", dstFactor: "one" } }
                : undefined;
        const desc = {
            layout: device.createPipelineLayout({ bindGroupLayouts: p.binds.length ? [p.layout] : [] }),
            vertex: { module, entryPoint: "vs_main", buffers: p.vbufs.filter(Boolean) },
            fragment: { module, entryPoint: "fs_main",
                targets: [{ format: FORMATS[p.colorFmt], blend }] },
            primitive: {
                topology: p.topology === "line" ? "line-list" : "triangle-list",
                cullMode: p.cull, frontFace: "ccw",
            },
            multisample: { count: p.samples },
        };
        if (p.hasDepth) {
            desc.depthStencil = {
                format: "depth32float",
                depthWriteEnabled: p.depth === "write",
                depthCompare: p.depth === "none" ? "always" : "less",
            };
        }
        p.gpu = device.createRenderPipeline(desc);
        return p;
    }

    function groupFor(id) {
        const g = groups.get(id);
        if (!g) fail("unknown group " + id);
        if (g.gpu) return g.gpu;
        const p = pipelineFor(g.pipe);
        const entries = [];
        for (const b of p.binds) {
            if (b[0] === "uniform") {
                const ub = buffers.get(g.uniform);
                if (!ub) fail("group " + id + " has no uniform buffer");
                entries.push({ binding: 0, resource: { buffer: ub.buf } });
            } else if (b[0] === "tex") {
                const slot = int(b[1], "slot");
                const t = g.tex.find(x => x.slot === slot);
                if (!t) fail("group " + id + " has no texture in slot " + slot);
                const tex = textures.get(t.tex);
                entries.push({ binding: 1 + 2 * slot,
                    resource: tex.tex.createView({ dimension: tex.dim === "cube" ? "cube" : "2d" }) });
                entries.push({ binding: 2 + 2 * slot, resource: samplers.get(t.smp) });
            }
        }
        g.gpu = device.createBindGroup({ layout: p.layout, entries });
        return g.gpu;
    }

    function encodeDraw(enc, d) {
        const p = pipelineFor(d.pipe);
        enc.setPipeline(p.gpu);
        if (d.group !== "-") enc.setBindGroup(0, groupFor(d.group));
        d.vbs.forEach((vb, slot) => enc.setVertexBuffer(slot, buffers.get(vb).buf));
        if (d.ibuf !== "-") {
            enc.setIndexBuffer(buffers.get(d.ibuf).buf, d.ifmt === "u16" ? "uint16" : "uint32");
            enc.drawIndexed(d.count, d.instances, d.first, d.baseVertex, d.firstInstance);
        } else {
            enc.draw(d.count, d.instances, d.first, d.firstInstance);
        }
    }

    const encoder = device.createCommandEncoder();
    for (const pass of passes) {
        const color = textures.get(pass.color);
        const att = {
            view: color.tex.createView(),
            loadOp: pass.load === "load" ? "load" : "clear",
            clearValue: pass.clear, storeOp: "store",
        };
        if (pass.resolve !== "-") att.resolveTarget = textures.get(pass.resolve).tex.createView();
        const desc = { colorAttachments: [att] };
        let depthInfo = null;
        if (pass.depth !== "-") {
            depthInfo = { fmt: textures.get(pass.depth) };
            desc.depthStencilAttachment = {
                view: textures.get(pass.depth).tex.createView(),
                depthClearValue: pass.depthClear, depthLoadOp: "clear", depthStoreOp: "store",
            };
        }
        const rp = encoder.beginRenderPass(desc);
        for (const item of pass.items) {
            if (item.bundle) {
                const be = device.createRenderBundleEncoder({
                    colorFormats: [FORMATS[color.fmt]],
                    depthStencilFormat: depthInfo ? "depth32float" : undefined,
                    sampleCount: pipes.get(item.bundle[0].pipe).samples,
                });
                for (const d of item.bundle) encodeDraw(be, d);
                rp.executeBundles([be.finish()]);
            } else {
                encodeDraw(rp, item);
            }
        }
        rp.end();
    }

    const out = textures.get(output);
    if (!out) fail("no output texture");
    if (out.fmt !== "rgba8") fail("output texture must be rgba8");
    const rowBytes = out.w * 4;
    const padded = Math.ceil(rowBytes / 256) * 256;
    const readback = device.createBuffer({
        size: padded * out.h, usage: GPUBufferUsage.COPY_DST | GPUBufferUsage.MAP_READ,
    });
    encoder.copyTextureToBuffer({ texture: out.tex },
        { buffer: readback, bytesPerRow: padded, rowsPerImage: out.h }, [out.w, out.h, 1]);
    device.queue.submit([encoder.finish()]);
    const err = await device.popErrorScope();
    if (err) fail("validation: " + err.message);
    await readback.mapAsync(GPUMapMode.READ);
    const src = new Uint8Array(readback.getMappedRange());
    const pixels = new Uint8Array(rowBytes * out.h);
    for (let y = 0; y < out.h; y++) {
        pixels.set(src.subarray(y * padded, y * padded + rowBytes), y * rowBytes);
    }
    readback.unmap();
    if (width && (out.w !== width || out.h !== height)) fail("output size differs from job size");
    await Deno.writeFile(outPath, pixels);
    const info = adapter.info ?? {};
    console.log("webgpu_host: rendered " + out.w + "x" + out.h + " on " +
        [info.vendor, info.architecture, info.description].filter(Boolean).join(" ").trim());
}

await main();
