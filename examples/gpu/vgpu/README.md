# vgpu compatibility corpus

This directory is Flow's executable compatibility target for the public examples at
<https://vgpu.sh/examples/>.

The goal is not to imitate screenshots manually. Each case should express the same
rendering or compute problem in Flow, run through Flow's own GPU pipeline, and have
a deterministic reference comparison where the upstream example can be captured
under controlled inputs.

## Contract

A compatibility case is complete only when:

1. the Flow source compiles through every backend required by that case;
2. the source uses Flow GPU/FSL APIs rather than embedding WGSL/MSL source;
3. render size, time, camera, seed, textures and other inputs are fixed;
4. the produced frame or numerical result is compared against the reference;
5. exact RGBA equality is required for backend-stable cases, otherwise the test
   records an explicit numerical/perceptual tolerance and why exact equality is
   not portable.

## Backend model

Fullscreen FSL has two source generators from the same parsed AST, both in
flowc (`compiler/src/shader_dsl.flow`):

```text
"shader fill"
    -> flowc FLOWC_SHADER=metal  -> MSL / Metal
    -> flowc FLOWC_SHADER=wgsl   -> WGSL / WebGPU
```

Flow already has a separate `@gpu` compute path with Metal and WGSL backends. The
compatibility work should converge these surfaces around shared resources and
pipeline declarations rather than create another shader language.

The browser host renders FSL WGSL into an offscreen `rgba8unorm` texture, copies it
to a readback buffer and removes WebGPU row padding before comparison. This keeps
the conformance bytes independent of canvas DPR, swap-chain format and browser
compositing. `compareRgba` then provides an exact byte comparison primitive.

## Cases

| Case | Flow source | Metal | WGSL | Reference comparison |
| --- | --- | --- | --- | --- |
| Gradient | `gradient.flow` | emit + exact-pixel | emit + exact-pixel | captured `rgba8unorm` at 160×90, `time=0` |
| MNIST | `mnist.flow` | source stub | source stub | `UNSUPPORTED` (`tensor-model-execution`) |
| Depth | `depth_estimation.flow` | source stub | source stub | `UNSUPPORTED` (`tensor-model-execution`) |
| Instanced rendering | `instanced_rendering.flow` | drawn on device | drawn on device | probes, Metal = WebGPU, captured frame at 128×72 |
| Batch rendering | `batch_rendering.flow` | drawn on device | drawn on device | probes, Metal = WebGPU, captured frame at 128×72 |
| Environment map | `environment_map.flow` | drawn on device | drawn on device | probes, Metal = WebGPU, captured frame at 128×72 |
| Earth | `earth.flow` | drawn on device | drawn on device | probes, Metal = WebGPU, captured frame at 128×72 |
| Anti-aliasing | `anti_aliasing.flow` | drawn on device | drawn on device | probes, Metal = WebGPU, captured frame at 128×72 |
| Clipping | `clipping.flow` | drawn on device | drawn on device | probes, Metal = WebGPU, captured frame at 128×72 |
| Transmission | `transmission.flow` | drawn on device | drawn on device | probes, Metal = WebGPU, captured frame at 128×72 |

The seven render cases (#811) are Flow programs built on
`lib/stdlib/gpu_render.flow`. Each one declares typed textures, samplers,
vertex layouts and stage interfaces, builds its vertex and fragment stages
from typed shader expressions that emit WGSL and Metal together, and runs
headless: `./flow run examples/gpu/vgpu/earth.flow` draws the frame on the
Metal device and on a WebGPU adapter under Deno, then checks the program's
own pixel probes, that the two backends agree, and the captured frame in
`refs/`. The captured frames come from these programs, not from the
upstream pages. See [GPU render jobs](../../../docs/library/gpu-render.md).

Still open in the corpus: storage textures, multi-pass compute,
workgroup memory and barriers, and tensor and model execution.

## Run the suite

The compatibility command is the conformance runner, not a visual gallery:

```bash
./flow gpu test --suite vgpu --all-backends
```

That prints `EXACT` / `TOLERANCE` / `NUMERICAL` / `UNSUPPORTED` / `FAIL` per
case and backend, with dimensions, inputs and max error. It exits non-zero on
unexpected `FAIL`. Docs: [vgpu conformance](../../../docs/gpu/vgpu-conformance.md).

Capture (rewrite frozen references; not the ordinary shader window):

```bash
./flow gpu test --suite vgpu --backend webgpu --case gradient --capture-reference
```

Metal uses the existing FSL command:

```bash
./flow shader examples/gpu/vgpu/gradient.flow --name vgpu_gradient
```

WGSL emission uses:

```bash
./flow shader examples/gpu/vgpu/gradient.flow --wgsl --name vgpu_gradient
```

Build a browser runner backed by deterministic offscreen WebGPU readback:

```bash
./flow tool wasm_crossings shader examples/gpu/vgpu/gradient.flow \
    --name vgpu_gradient --size 640x360
python3 -m http.server -d build/webgpu-shader 8000
```

The generated WebGPU entry points are `flow_shader_vertex` and
`vgpu_gradient_frag`. The suite parameters used for reference comparisons live in
`manifest.json`. The captured gradient bytes live in `refs/`.
