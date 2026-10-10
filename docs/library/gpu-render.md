# GPU render jobs

Four modules take a Flow program from typed GPU descriptors to pixels on
Metal and WebGPU (#811):

| Module | What it holds |
|---|---|
| `lib/stdlib/gpu_shader.flow` | typed shader expressions that emit WGSL and Metal together |
| `lib/stdlib/gpu_render.flow` | render jobs: buffers, textures, samplers, pipelines, passes, draws, probes |
| `lib/stdlib/gpu_render_host.flow` | runs a job on both backends and checks the frames |
| `lib/stdlib/gpu_scene.flow` | column-major matrices in the Metal and WebGPU clip convention, and meshes |

The descriptors are the ones in
[GPU resource types](gpu-resource-types.md): `GpuTextureDesc`,
`GpuSamplerDesc`, `GpuVarying`, `GpuVertexAttribute`, `GpuRenderTargets`,
`GpuTextureBinding` and `GpuDrawDesc`. flowc checks them at compile time
when their fields are constants. Every job call checks them again with the
run-time validators, so a descriptor built from run-time values is caught
too.

## Stages

A pipeline declares its stage interface once: the varyings the vertex
stage writes and the fragment stage reads, the vertex attributes, the
texture bindings and the size of the uniform block. Each stage is then
built from typed expressions:

```flow
import "stdlib/gpu_render_host.flow"

function main() -> i32 {
    let job: ptr<GpuJob> = gpu_job_new("one_triangle", 64, 64, gpu_job_root())
    let color: GpuTextureDesc = GpuTextureDesc {
        dimension: GPU_TEX_2D, format: GPU_FORMAT_RGBA8,
        width: 64, height: 64, layers: 1, samples: 1,
        usage: GPU_USE_COLOR_ATTACHMENT
    }
    let targets: GpuRenderTargets = GpuRenderTargets { color: color, depth: color, has_depth: false }
    let uv: GpuVarying = GpuVarying { location: 0, scalar: GPU_SCALAR_F32, components: 2, interpolation: GPU_INTERPOLATE_PERSPECTIVE }
    let vs_out: array<GpuVarying, 1> = [uv]
    let fs_in: array<GpuVarying, 1> = [uv]
    let p: ptr<GpuPipeline> = gpu_pipeline_new(job, "tri", &vs_out[0], 1, &fs_in[0], 1)
    gpu_pipeline_targets(p, targets)

    let vs: ptr<GxFn> = gpu_pipeline_vs(p)
    let vid: GxExpr = gx_f32_of(gx_vertex_index(vs))
    let x: GxExpr = gx_let(vs, gx_sub(gx_mul(vid, gx_f(0.8)), gx_f(0.8)))
    gx_out_position(vs, gx_vec4(x, gx_mul(x, x), gx_f(0.0), gx_f(1.0)))
    gx_out(vs, 0, gx_vec2(x, gx_f(0.5)))

    let fs: ptr<GxFn> = gpu_pipeline_fs(p)
    let c: GxExpr = gx_in(fs, 0)
    gx_out_color(fs, gx_vec4(gx_x(c), gx_y(c), gx_f(0.3), gx_f(1.0)))
    let _id: i32 = gpu_pipeline_finish(p)

    let t: i32 = gpu_texture(job, color, null)
    gpu_pass(job, t, 0 - 1, 0 - 1, 0.0, 0.0, 0.0, 1.0)
    let none: array<i32, 1> = [0]
    gpu_draw(job, p, 0 - 1, &none[0], 0, 3, 1, 0, 0)
    gpu_output(job, t)
    return gpu_job_run(job)
}
```

`gx_*` calls check operand types as the stage is built. Adding a vec3 to a
vec2, writing a vec2 into a vec3 varying, reading a varying the fragment
stage did not declare, or sampling a cube map with a 2D coordinate records
an error on the stage. `gpu_pipeline_finish` then emits nothing and the job
reports the error. A stage that never writes its position, its colour or
one of its declared varyings is an error too.

The expressions cover arithmetic with scalar broadcast, matrix times
vector, comparisons and `select`, swizzles, constructors, the common
built-in functions (`dot`, `cross`, `normalize`, `reflect`, `refract`,
`mix`, `clamp`, `smoothstep`, `pow` and others), texture sampling,
`discard`, and the `vertex_index`, `instance_index`, `front_facing` and
fragment position built-ins. `gx_let` names a value so it is computed once.

## Jobs

`gpu_job_write` stores the frame as a directory under `build/gpu_render/`
(or `$FLOW_GPU_JOB_ROOT`): `job.txt` with one command per line, the
emitted `.wgsl` and `.metal` stages, the buffer and texture bytes, and
`probes.txt`. The command format is listed at the top of
`lib/stdlib/gpu_render.flow`.

A job checks what the descriptors alone cannot: a pipeline's colour format
and sample count against the pass it draws in, a depth target on both or
neither, a bind group that fills every texture slot with the declared
kind of texture, a pass that samples a texture it renders into, a
multisampled pass without a resolve target, and draw counts against the
index buffer.

## Hosts

| Backend | Host | Needs |
|---|---|---|
| Metal | `runtime/gpu_render_metal.m` | macOS, `xcrun clang`; built into `build/gpu_render/` on first use |
| WebGPU | `tools/gpu_render/webgpu_host.mjs` | Deno with a WebGPU adapter |

Both replay the same job offscreen and write the output texture as tightly
packed RGBA8. Neither carries shader source of its own. A host whose
toolchain or device is missing reports `UNSUPPORTED`.

## Checking a frame

`gpu_job_run` renders on each backend in `FLOW_GPU_BACKENDS` (default
`metal,webgpu`) and checks each frame three ways:

1. Probes: facts the program states about its own frame, such as a
   background pixel, a dominant hue, one pixel brighter than another, or
   a count of partially covered edge pixels in a rectangle.
2. Backends: Metal and WebGPU agree within 3 per channel, allowing up to 24
   pixels beyond that.
3. Reference: the frame matches `examples/gpu/vgpu/refs/NAME_WxH.rgba8.hex`
   with the same tolerance. `FLOW_GPU_CAPTURE=1` rewrites it.

It prints one line per backend:

```text
GPU_RENDER earth [metal] PASS maxError=0
GPU_RENDER earth [webgpu] PASS maxError=0
```

`flow gpu test --suite vgpu` runs the corpus cases whose renderer is
`render-job` this way. See [vgpu conformance](../gpu/vgpu-conformance.md).

## The vgpu cases

| Case | Program | What it exercises |
|---|---|---|
| Instanced rendering | `examples/gpu/vgpu/instanced_rendering.flow` | 125,000 instances of one cube, a per-instance stream, flat varyings |
| Batch rendering | `examples/gpu/vgpu/batch_rendering.flow` | four primitive ranges in one mesh, base vertex, first instance, a WebGPU render bundle |
| Environment map | `examples/gpu/vgpu/environment_map.flow` | a cube map as background and as the source of reflections |
| Earth | `examples/gpu/vgpu/earth.flow` | two textures, an rgba16f target, additive blending, bloom and tone mapping |
| Anti-aliasing | `examples/gpu/vgpu/anti_aliasing.flow` | no AA, MSAA 4x resolve, SSAA 2x and an FXAA-style blend side by side |
| Clipping | `examples/gpu/vgpu/clipping.flow` | signed-distance discard, front and back faces, MSAA with depth |
| Transmission | `examples/gpu/vgpu/transmission.flow` | a texture both rendered and sampled, screen-space refraction, Fresnel |

Run one with `./flow run examples/gpu/vgpu/earth.flow`.

The references are frames these programs rendered, captured once on Apple
silicon. They pin the output of the Flow scene. They are not screenshots
of the upstream vgpu pages, whose scenes use photographs, animation and
interaction that a fixed frame does not reproduce.
