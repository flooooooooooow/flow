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

Fullscreen FSL now has two source generators from the same parsed AST:

```text
"shader fill / vertex / fragment"
    -> shader_dsl.py
       -> shader_codegen.py       -> MSL / Metal
       -> shader_codegen_wgsl.py  -> WGSL / WebGPU
```

Flow already has a separate `@gpu` compute path with Metal and WGSL backends. The
compatibility work converges these surfaces around shared resources and
pipeline declarations rather than creating another shader language.

The browser host renders FSL WGSL into an offscreen `rgba8unorm` texture, copies it
to a readback buffer and removes WebGPU row padding before comparison. This keeps
the conformance bytes independent of canvas DPR, swap-chain format and browser
compositing. `compareRgba` then provides an exact byte comparison primitive.

## Cases

| Case | Flow source | Metal | WGSL | Reference comparison |
| --- | --- | --- | --- | --- |
| Gradient | `gradient.flow` | ready | ready | upstream reference bytes pending |
| Instanced Rendering | `instanced_rendering.flow` | ready | ready | upstream reference bytes pending |
| Batch Rendering | `batch_rendering.flow` | ready | ready | upstream reference bytes pending |
| Environment Map | `environment_map.flow` | ready | ready | upstream reference bytes pending |
| Earth | `earth.flow` | ready | ready | upstream reference bytes pending |
| Anti-Aliasing | `anti_aliasing.flow` | ready | ready | upstream reference bytes pending |
| Clipping | `clipping.flow` | ready | ready | upstream reference bytes pending |
| Transmission Material | `transmission_material.flow` | ready | ready | upstream reference bytes pending |

## Run a case

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

The suite parameters used for reference comparisons live in `manifest.json`.
