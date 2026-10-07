# Typed GPU resources: P1 descriptor contract

The source library `lib/stdlib/gpu_resource_types.flow` introduces a
backend-neutral descriptor vocabulary for **issue #811**. Its validation
functions are pure Flow and work without Metal, WebGPU or GPU hardware.

`GpuTextureDesc` validates dimensions, cubemap faces, storage usage, depth
versus color attachment formats, and multisampling. Its byte count rejects
invalid descriptors with `0`. `GpuSamplerDesc` validates filtering and
address modes. `GpuVarying` plus `gpu_stage_links` check unique shader
locations and matching scalar type, width and interpolation (including
mandatory flat interpolation for integers). `GpuVertexAttribute` checks
that attribute bytes fit within a vertex stride without out-of-bounds
offset arithmetic.

Example:

```flow
import "stdlib/gpu_resource_types.flow"

function main() -> i32 {
    let color: GpuTextureDesc = GpuTextureDesc {
        dimension: GPU_TEX_2D,
        format: GPU_FORMAT_RGBA8,
        width: 160, height: 90, layers: 1, samples: 1,
        usage: GPU_USE_SAMPLED | GPU_USE_COLOR_ATTACHMENT
    }
    if not gpu_texture_valid(color) { return 1 }
    return 0
}
```

Run the CPU-only regression with:

```bash
./flow test-runtime tests/lang/test_gpu_resource_types.flow
```

**Scope boundary:** These checks are API-level prevalidation and do **not**
yet constitute compile-time errors for GPU source declarations, renderer
resource lowering, a GPU-hazard DAG, or native Metal/WebGPU draw execution.
The #811 acceptance tests (instancing, Earth, cubemaps, anti-aliasing and
materials on both backends) remain open. Descriptor limits are conservative
portability defaults. They are not negotiated per device.

## Stage code generation and draw validation

`lib/stdlib/gpu_stage_codegen.flow` adds validated render-pass descriptors
and real, nonempty Metal/WGSL sampled-texture shaders:

- `GpuDrawDesc` validates indexed and instanced draw counts, index-buffer
  capacity, supported index types and signed offset overflow.
- `GpuRenderTargets` checks color/depth format, attachment usage,
  dimensions and matching MSAA sample counts.
- `GpuSampledPipeline` links a typed sampled 2D/cubemap texture, sampler,
  render targets and matching stage varyings. Cubemap coordinates require
  three-component floating-point varyings.
- `gpu_emit_wgsl_sampled` and `gpu_emit_metal_sampled` generate vertex
  position fetches and fragment texture sampling for the same descriptor.
  Invalid descriptors produce an empty result instead of a no-op shader.

Regression programs (do not require a GPU):

```sh
./flow run tests/lang/test_gpu_resource_types.flow
./flow run tests/lang/test_gpu_stage_codegen.flow
```

These are **not yet** language-level compile-time diagnostics for arbitrary
render source. A working Metal/WebGPU pipeline host must still create render
pipelines, configure vertex/index/instance bindings, build and bind textures
and samplers, create depth/MSAA targets, submit draws and read back images.
The full instancing, Earth, cubemap and materials compatibility corpus from
#811 remains unverified; generated source alone is not GPU rendering parity.

## Browser WebGPU draw/readback host

The same Flow-produced WGSL stage pair can now be **executed** by
`renderFlowSampledDraw(device, descriptor)` in
`wasm/crossing_assets/gpu-sampled-draw.mjs`, also exposed by the
site's `webgpu-host.js`. Unlike a shader-emission check, this host
creates the texture and sampler, uploads a float4 position buffer,
configures the actual WebGPU render pipeline, submits an indexed or
non-indexed *instanced* draw, resolves 4x MSAA when requested, and reads
back tightly packed `rgba8unorm` pixels. Optional depth32float matches
the color target size and samples. Cubemaps upload exactly six faces.

```js
import { getDevice, renderFlowSampledDraw } from "./webgpu-host.js";

const {device} = await getDevice();
const result = await renderFlowSampledDraw(device, {
  wgsl: generatedWgslFromFlow,
  positions: new Float32Array([
    -1,-1,0,1,  1,-1,0,1,  0,1,0,1
  ]),
  indices: new Uint16Array([0,1,2]),
  instances: 4,
  textureRGBA: sourceRgba8,
  textureWidth: 256, textureHeight: 256,
  width: 160, height: 90,
  depth: true, samples: 4
});
console.log(result.execution, result.rgba);
```

The `generatedWgslFromFlow` input must be emitted by
`gpu_emit_wgsl_sampled`; the host deliberately does not accept a
separate hand-coded shader as the Flow implementation. Verify browser
support with a real `navigator.gpu` device.

Host-side mocks and strict invalid-input tests:

```sh
node --test tests/webgpu/sampled-draw.test.mjs
```

**Not yet complete:** A compiler-driven glue layer from arbitrary Flow
render-stage declarations to these descriptors, WebGPU/Metal feature
negotiation beyond the portable baseline, and frozen upstream vgpu
reference-image comparisons on live devices remain. Real shader execution
is not the same as established vgpu pixel parity.

## Flow-generated WebGPU textured draw smoke test

A complete, inspectable Flow-to-browser integration now lives in:

- `examples/gpu/vgpu/sampled_quad.flow`: typed sample/depth/color
  resources, nearest sampler, varying contract, real generated WGSL and MSL
  vertex/fragment programs.
- `tools/gpu_graph/export_sampled.mjs`: compiles/runs that exact Flow
  source to export both shaders, without writing replacement WGSL/Metal.
- `site/wasm-crossings/gpu/sampled-quad.html`: executes the emitted WGSL on
  a live WebGPU device using the checked sampler/geometry host, instanced
  draws, 4× MSAA/depth, and a 1×1 solid-color reference texture. It
  checks the framebuffer centre pixel for exact RGBA equality.

From the project root:

```sh
node tools/gpu_graph/export_sampled.mjs
python3 -m http.server 8000 --directory site
```

Visit `http://localhost:8000/wasm-crossings/gpu/sampled-quad.html`
on a WebGPU-capable machine and select **Run on WebGPU**.

The generated shader modules live under
`site/wasm-crossings/gpu/generated/`. The page deliberately fails when
they are absent, rather than substituting an inline shader. The reference
is a deterministic single-color texture. It is not an upstream vgpu screenshot.

A unit-test/mock-device result must not be mistaken for evidence of
physical WebGPU rendering. The remaining #811 acceptance work includes
driver/device runs, a native Metal render host, general indexed vertex
layouts and material/lighting pipelines, upstream vgpu reference images
for instancing/Earth/cubemaps/clipping/transmission, and compile-time
diagnostics integrated into arbitrary Flow GPU declarations.
