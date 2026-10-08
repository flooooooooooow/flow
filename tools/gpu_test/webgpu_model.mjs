// WebGPU half of the vgpu model cases (#814), run by `flow gpu test`.
//
//   deno run --allow-read tools/gpu_test/webgpu_model.mjs MODEL KERNEL_DIR REFERENCE
//
// MODEL is mnist or depth. KERNEL_DIR holds the WGSL and the reflection
// manifest that `tools/gpu/main.flow --crossing-manifest` wrote for the
// example (manifest.json next to NAME.wgsl). REFERENCE is the "reference"
// line the Flow example printed: its host result, one value per output.
//
// The stages are the example's own @gpu kernels, chained over persistent
// device buffers by runFlowKernelChain (wasm/crossing_assets/
// gpu-kernel-chain.mjs). The model layers that the Metal runtime runs as
// gpu_tensor kernels run here as the example's dense and activation
// kernels. Inputs match the tensor_fill calls in each example's main.
//
// Prints WEBGPU_DEVICE_EXECUTED, maxAbs and match 1 or 0. Exits 0 on a
// match, 1 on a mismatch or a host error, 2 when there is no adapter.

const [model, dir, referenceLine] = Deno.args;
const root = new URL("../../", import.meta.url);
const {runFlowKernelChain} = await import(new URL("wasm/crossing_assets/gpu-kernel-chain.mjs", root).href);

const manifest = JSON.parse(await Deno.readTextFile(dir + "/manifest.json"));
const kernels = Object.fromEntries(manifest.map((k) => [k.kernel, k]));
const wgsl = {};
for (const k of manifest) {
  wgsl[k.kernel] = await Deno.readTextFile(dir + "/" + k.file);
}

function fill(n, v) {
  return new Float32Array(n).fill(v);
}

function stage(kernel, bindings, scalars, count, required) {
  const s = {descriptor: kernels[kernel], wgsl: wgsl[kernel], bindings, scalars, count};
  if (required) {
    s.allowNonlinear = true;
    s.requiredElements = required;
  }
  return s;
}

// One output row: M = 1, so the dense kernels dispatch one thread.
function plan(name) {
  if (name === "mnist") {
    const inDim = 784, hidden = 16, classes = 10;
    return {
      out: "probs",
      resources: {
        raw: {length: inDim, initial: fill(inDim, 128.0)},
        norm: {length: inDim},
        w1: {length: inDim * hidden, initial: fill(inDim * hidden, 0.01)},
        h1: {length: hidden},
        h1r: {length: hidden},
        w2: {length: hidden * classes, initial: fill(hidden * classes, 0.05)},
        logits: {length: classes},
        probs: {length: classes},
      },
      stages: [
        stage("mnist_preprocess", {raw: "raw", norm: "norm"}, {n: inDim}, inDim),
        stage("mnist_dense_layer", {input: "norm", weights: "w1", output: "h1"},
              {M: 1, K: inDim, N: hidden}, 1, {input: inDim, weights: inDim * hidden, output: hidden}),
        stage("mnist_postprocess", {logits: "h1", probs: "h1r"}, {n: hidden}, hidden),
        stage("mnist_dense_layer", {input: "h1r", weights: "w2", output: "logits"},
              {M: 1, K: hidden, N: classes}, 1, {input: hidden, weights: hidden * classes, output: classes}),
        stage("mnist_postprocess", {logits: "logits", probs: "probs"}, {n: classes}, classes),
      ],
    };
  }
  if (name === "depth") {
    const dim = 64, out = 64;
    return {
      out: "color",
      resources: {
        img: {length: dim, initial: fill(dim, 0.5)},
        feat: {length: dim},
        w: {length: dim * out, initial: fill(dim * out, 0.02)},
        depth: {length: out},
        color: {length: out},
      },
      stages: [
        stage("depth_feature_extract", {image: "img", features: "feat"}, {n: dim}, dim),
        stage("depth_projection_layer", {features: "feat", weights: "w", depth_map: "depth"},
              {M: 1, K: dim, N: out}, 1, {features: dim, weights: dim * out, depth_map: out}),
        stage("depth_colormap_tint", {depth_map: "depth", colormap: "color"}, {n: out}, out),
      ],
    };
  }
  throw new Error("unknown model " + name);
}

const p = plan(model);
const reference = referenceLine.trim().split(/\s+/).filter((t) => t !== "reference").map(Number);

const adapter = await navigator.gpu?.requestAdapter();
if (!adapter) {
  console.log("NO_ADAPTER");
  Deno.exit(2);
}
const device = await adapter.requestDevice();
let result;
try {
  result = await runFlowKernelChain(device, {resources: p.resources, stages: p.stages, readback: [p.out]});
} catch (e) {
  console.log("ERROR " + e.message);
  Deno.exit(1);
}
const got = result.outputs[p.out];
let maxAbs = 0;
let ok = got.length === reference.length && result.execution === "webgpu-device";
for (let i = 0; i < Math.min(got.length, reference.length); i++) {
  const d = Math.abs(got[i] - reference[i]);
  if (!(d <= maxAbs)) maxAbs = d;
}
if (!(maxAbs <= 0.0001)) ok = false;
if (result.execution === "webgpu-device") console.log("WEBGPU_DEVICE_EXECUTED");
console.log("maxAbs " + maxAbs);
console.log("match " + (ok ? 1 : 0));
Deno.exit(ok ? 0 : 1);
