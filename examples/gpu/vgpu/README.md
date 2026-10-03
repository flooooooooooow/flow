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

Fullscreen FSL and multi-pass GPU graph rendering now share a unified resource and pass graph (`src/flow/gpu_graph.py`):

```text
"gpu frame / gpu resource"
    -> gpu_graph.py
       -> generate_metal()       -> MSL / Metal Orchestration
       -> generate_webgpu_js()   -> WGSL / WebGPU JS Orchestration
```

Flow already has a separate `@gpu` compute path with Metal and WGSL backends. The
compatibility work converges these surfaces around shared resources, ping-pong targets,
storage textures/buffers, and pipeline declarations rather than creating another shader language.

## Cases

| Case | Flow source | Metal | WGSL | Reference comparison |
| --- | --- | --- | --- | --- |
| Gradient | `gradient.flow` | source-ready | offscreen renderer ready | upstream reference bytes pending |
| Fluid | `fluid.flow` | graph-ready | graph-ready | numerical tolerance (1e-4) |
| FFT Ocean | `fft_ocean.flow` | graph-ready | graph-ready | numerical tolerance (1e-4) |

## Run the cases

Metal uses the existing FSL command:

```bash
./flow shader examples/gpu/vgpu/gradient.flow --name vgpu_gradient
```

WGSL emission uses:

```bash
python3 scripts/emit_fsl_wgsl.py examples/gpu/vgpu/gradient.flow --name vgpu_gradient
```

Build a browser runner backed by deterministic offscreen WebGPU readback:

```bash
python3 wasm/flow_webgpu_shader.py examples/gpu/vgpu/gradient.flow \
    --name vgpu_gradient --size 640x360
python3 -m http.server -d build/webgpu-shader 8000
```

The generated WebGPU entry points are `flow_shader_vertex` and
`vgpu_gradient_frag`. The suite parameters used for reference comparisons live in
`manifest.json`.
