# vgpu parity track

Flow should be able to express, render and compute every public vgpu example without
embedding vendor shader source. vgpu is the compatibility floor; Flow's own GPU,
simulation, typed-units and photoreal shader examples remain the surface we extend
beyond it.

## Definition of parity

Parity is evidence, not a screenshot claim. Every imported case records fixed
inputs and produces either a deterministic image or deterministic numerical output.
The harness compares Flow against the upstream reference. Exact pixel equality is
the default for simple fragment cases. Cases whose result is legitimately sensitive
to backend floating-point, filtering, model kernels or texture formats must declare
a narrow tolerance in the case manifest.

The compatibility corpus lives in `examples/gpu/vgpu/`.

## Architecture

Flow already has two useful halves:

* FSL `shader fill` lowers to Metal and powers the shader galleries.
* `@gpu` functions lower to Metal and WGSL for compute kernels.

This track closes the gap rather than inventing a third GPU stack.

```text
                    Flow source
                        |
            +-----------+-----------+
            |                       |
       shader fill                  @gpu
            |                       |
       FSL parsed AST          Flow compiler AST
            |                       |
      +-----+-----+            +----+----+
      |           |            |         |
     MSL         WGSL         MSL       WGSL
      |           |            |         |
    Metal       WebGPU       Metal     WebGPU
```

The initial branch adds the missing FSL -> WGSL edge. The next architecture step is
shared GPU resource and pipeline declarations so fragment, vertex and compute stages
can exchange typed buffers/textures without host-side stringly glue.

## Capability ladder

### P0: fullscreen fragment parity

Needed: FSL AST, MSL backend, WGSL backend, deterministic uniforms and reference
capture.

Representative cases: gradient, black-hole/fractal-style fullscreen effects and
other procedural fragments.

Exit condition: the simple upstream fragment examples render from the same Flow
source on Metal and WebGPU, with pixel comparison in the compatibility harness.

### P1: textures, samplers and render geometry

Add typed GPU resources and stage declarations:

```flow
let albedo = gpu.texture<rgba8unorm>(size)
let linear = gpu.sampler(filter: linear)

shader vertex scene(v: Vertex) -> RasterVertex { ... }
shader fragment scene(in: RasterVertex, albedo, linear) -> vec4 { ... }
```

Required surface: sampled textures, storage textures, samplers, vertex/index
buffers, vertex attributes, instance id, indexed/instanced draw, render state,
depth/stencil, MSAA, cubemaps and render targets.

Representative compatibility cases: instanced rendering, batch rendering,
environment map, Earth, anti-aliasing, clipping and transmission/material scenes.

### P2: render/compute graph

Make pass ordering and resource hazards first-class rather than hidden host calls:

```flow
gpu frame {
    compute advect(velocity.read, velocity.next)
    compute divergence(velocity.next, divergence)

    repeat 20 {
        compute pressure(pressure.read, divergence, pressure.next)
        pressure.swap()
    }

    render surface {
        draw fluid(velocity.next, dye)
    }
}
```

Required surface: dispatch dimensions, storage buffers/textures, workgroup memory,
barriers, ping-pong resources, explicit read/write access, transient resources and
compile-time hazard validation.

Representative compatibility cases: fluid, FFT ocean, FFT ocean surface, air
painting and radiance cascades.

### P3: GPU tensors and model execution

Connect Flow tensor/model types to the same GPU resource model rather than creating
an inference-only runtime. The user-facing model should permit ordinary Flow kernels
before/after imported model execution without copies when the backend allows it.

Representative compatibility cases: MNIST classifier and depth estimation.

### P4: backend-independent compatibility runner

Target command:

```text
flow gpu test --suite vgpu --backend metal
flow gpu test --suite vgpu --backend webgpu
flow gpu test --suite vgpu --all-backends
```

Each case should print one of `EXACT`, `TOLERANCE`, `NUMERICAL`, `UNSUPPORTED` or
`FAIL`, together with the measured error and the capability that blocks unsupported
cases.

## Resource IR

The next compiler abstraction should be small and structural. A candidate internal
model is:

```text
GpuModule
  resources[]
    Buffer(element, access, lifetime)
    Texture(dim, format, access, lifetime)
    Sampler(filter, address)
  stages[]
    Vertex(entry, inputs, outputs, resources)
    Fragment(entry, inputs, outputs, resources)
    Compute(entry, workgroup_size, resources)
  passes[]
    RenderPass(...)
    ComputePass(...)
```

This should be an IR/data model, not new syntax by itself. FSL and normal Flow can
both lower into it. Backend emitters then map the same resource layout to Metal,
WGSL/WebGPU and later SPIR-V/Vulkan.

## Correctness rules worth making compile-time Flow features

Flow can beat a thin WebGPU wrapper by rejecting GPU mistakes before runtime:
resource access must agree with shader use; a pass cannot sample an attachment it is
simultaneously writing unless explicitly supported; ping-pong aliases cannot bind
the same physical resource to conflicting roles; workgroup-shared memory stays
within backend limits; vertex/fragment varyings agree structurally; texture format
and sampled value types agree; uniform layouts are backend-compatible; and pass
hazards produce a dependency edge or a compiler error.

## Performance comparison

Visual parity alone is insufficient for the competitive page. Once a case is
correct, record CPU submission time, GPU frame time, transient allocation count,
pipeline creation/cache behavior, upload bytes and dispatch/draw counts. Compare
warm steady-state separately from startup.

Flow should only claim a performance win where measurements support it. The first
engineering advantage we can establish before raw timing wins is less duplicated
host/shader representation: resource and stage types live in one language and are
checked together.

## Initial implementation landed by this track

The first slice adds `src/flow/shader_codegen_wgsl.py`, which consumes the existing
FSL AST and emits a WebGPU-compatible fullscreen vertex/fragment module, including
FSL helper functions and standard noise/palette functions. `gradient.flow` is the
first vgpu compatibility fixture, and unit tests cover WGSL generation, helper
functions, loops, named output and the required color assignment contract.
