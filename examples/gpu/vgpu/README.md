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
shader fill
    -> shader_dsl.py
       -> shader_codegen.py       -> MSL / Metal
       -> shader_codegen_wgsl.py  -> WGSL / WebGPU
```

Flow already has a separate `@gpu` compute path with Metal and WGSL backends. The
compatibility work should converge these surfaces around shared resources and
pipeline declarations rather than create another shader language.

## Cases

| Case | Flow source | Metal | WGSL | Reference comparison |
| --- | --- | --- | --- | --- |
| Gradient | `gradient.flow` | source-ready | source-ready | pending capture harness |

The next tranche should deliberately exercise missing capabilities instead of
adding only fragment effects: textures/samplers, vertex and index buffers,
instancing, storage textures, multi-pass compute, depth/stencil, cubemaps,
workgroup memory/barriers, and tensor/model execution.

## Run the first case

Metal uses the existing FSL command:

```bash
./flow shader examples/gpu/vgpu/gradient.flow --name vgpu_gradient
```

WGSL emission uses:

```bash
python3 scripts/emit_fsl_wgsl.py examples/gpu/vgpu/gradient.flow --name vgpu_gradient
```

The generated WebGPU entry points are `flow_shader_vertex` and
`vgpu_gradient_frag`.
