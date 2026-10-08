# GPU descriptor errors

flowc checks the GPU descriptor structs of
[`gpu_resource_types` and `gpu_stage_codegen`](../library/gpu-resource-types.md)
while it type checks a program. A texture whose format does not allow its
usage, a binding whose access the texture was not created for, or a
fragment input with no matching vertex output is a compile error with a
code from the table below.

The check applies when a descriptor is a compile-time constant: a struct
literal whose fields fold to integers through literals, module `const`
values, `|`, `&`, `+`, `-`, `*`, casts, record updates and immutable `let`
bindings. A field that comes from a parameter, a `let mut` or a call does
not fold, and the rules that read it are skipped. The library validators
(`gpu_texture_valid`, `gpu_stage_links` and the rest) still run when the
program runs and reject those descriptors there.

The rules are the library validators, applied at compile time. A program
the checker accepts can still fail a validator at run time, through a
value that did not fold. A descriptor the checker rejects always fails its
validator.

Only the structs declared in `lib/stdlib/gpu_resource_types.flow` and
`lib/stdlib/gpu_stage_codegen.flow` are checked. A program's own struct
with the same name is left alone.

## Message format

```text
FILE:LINE:COL: error: [GPU004] GpuTextureDesc field 'usage': a depth32f texture cannot have usage color_attachment
```

The position is the field that breaks the rule. Stage-interface errors
point at the fragment input (or the vertex output declared twice) and name
the call:

```text
FILE:LINE:COL: error: [GPU061] gpu_stage_links: fragment input at location 1 field 'components' is 4 but the vertex output has 3
```

## Codes

| Code | Struct | Rule |
|------|--------|------|
| GPU001 | GpuTextureDesc | `dimension` is `GPU_TEX_2D` or `GPU_TEX_CUBE` |
| GPU002 | GpuTextureDesc | `format` is rgba8, rgba16f or depth32f |
| GPU003 | GpuTextureDesc | `usage` is a nonempty set of `GPU_USE_*` bits |
| GPU004 | GpuTextureDesc | the format allows the usage: depth32f needs depth_attachment or sampled and has no color_attachment or storage; only depth32f has depth_attachment; a multisampled texture has no storage |
| GPU005 | GpuTextureDesc | `samples` is 1, 2, 4 or 8; a multisampled texture is 2d with one layer and has color_attachment or depth_attachment |
| GPU006 | GpuTextureDesc | a cube texture has square faces and a multiple of 6 layers |
| GPU007 | GpuTextureDesc | width and height are 1..16384, layers 1..2048 |
| GPU010 | GpuSamplerDesc | `min_filter` and `mag_filter` are nearest or linear |
| GPU011 | GpuSamplerDesc | `address_u`, `address_v`, `address_w` are clamp or repeat |
| GPU020 | GpuVarying | `location` is 0..31 |
| GPU021 | GpuVarying | `components` is 1..4 |
| GPU022 | GpuVarying | `scalar` is f32, i32 or u32 and `interpolation` is perspective or flat |
| GPU023 | GpuVarying | an i32 or u32 varying uses flat interpolation |
| GPU030 | GpuVertexAttribute | the attribute's bytes fit the stride at its offset |
| GPU031 | GpuVertexAttribute | location 0..31, 1..4 components, 2- or 4-byte scalars, stride 1..2048, offset not negative |
| GPU040 | GpuRenderTargets | the color target has usage color_attachment and a color format |
| GPU041 | GpuRenderTargets | the depth target is depth32f with usage depth_attachment |
| GPU042 | GpuRenderTargets | the depth target has the color target's size and sample count |
| GPU050 | GpuSampledPipeline | the sampled texture has usage sampled |
| GPU051 | GpuSampledPipeline | the sampled texture is single-sample and has a color format |
| GPU052 | GpuSampledPipeline | the coordinate varying is f32 at location 0 with perspective interpolation, 2 components for a 2d texture and 3 for a cube |
| GPU055 | GpuTextureBinding | the access is one the usage allows: sampled for `GPU_ACCESS_SAMPLE`, storage for the storage accesses |
| GPU056 | GpuTextureBinding | a sample binding reads a single-sample color texture; a storage binding needs a single-sample 2d color texture |
| GPU057 | GpuTextureBinding | the vertex stage does not write a storage texture |
| GPU058 | GpuTextureBinding | slot 0..15, a nonempty set of `GPU_STAGE_*` bits, a known access |
| GPU060 | stage interface | every fragment input has a vertex output at its location |
| GPU061 | stage interface | the vertex output and fragment input agree on scalar, components and interpolation |
| GPU062 | stage interface | no stage declares a location twice |

The stage-interface rules run on calls to `gpu_stage_links(&outputs[0],
n_out, &inputs[0], n_in)` when both arrays are immutable array literals of
foldable `GpuVarying` values and both counts fold.

## Examples

A depth texture used as a color target (GPU004):

```flow expect-error
import "stdlib/gpu_resource_types.flow"

function main() -> i32 {
    let depth: GpuTextureDesc = GpuTextureDesc {
        dimension: GPU_TEX_2D, format: GPU_FORMAT_DEPTH32F,
        width: 64, height: 64, layers: 1, samples: 1,
        usage: GPU_USE_DEPTH_ATTACHMENT | GPU_USE_COLOR_ATTACHMENT
    }
    if gpu_texture_valid(depth) { return 0 }
    return 1
}
```

Fix: drop `GPU_USE_COLOR_ATTACHMENT`, or give the color target its own
rgba8 or rgba16f texture.

A storage binding on a texture created for sampling (GPU055):

```flow expect-error
import "stdlib/gpu_resource_types.flow"

function main() -> i32 {
    let image: GpuTextureDesc = GpuTextureDesc {
        dimension: GPU_TEX_2D, format: GPU_FORMAT_RGBA8,
        width: 64, height: 64, layers: 1, samples: 1,
        usage: GPU_USE_SAMPLED
    }
    let out: GpuTextureBinding = GpuTextureBinding {
        slot: 0, stages: GPU_STAGE_COMPUTE,
        access: GPU_ACCESS_STORAGE_WRITE, texture: image
    }
    if gpu_texture_binding_valid(out) { return 0 }
    return 1
}
```

Fix: add `GPU_USE_STORAGE` to the texture's usage, or bind it with
`GPU_ACCESS_SAMPLE`.

A fragment input that does not match the vertex output (GPU061):

```flow expect-error
import "stdlib/gpu_resource_types.flow"

function main() -> i32 {
    let normal_out: GpuVarying = GpuVarying {
        location: 1, scalar: GPU_SCALAR_F32,
        components: 3, interpolation: GPU_INTERPOLATE_PERSPECTIVE
    }
    let normal_in: GpuVarying = GpuVarying { ..normal_out, components: 4 }
    let vs: array<GpuVarying, 1> = [normal_out]
    let fs: array<GpuVarying, 1> = [normal_in]
    if gpu_stage_links(&vs[0], 1, &fs[0], 1) { return 0 }
    return 1
}
```

Fix: declare the same scalar type, component count and interpolation on
both sides of the location.

One failing program per code lives in `compiler/fixtures/typecheck_rules/`
(`gpu_*.flow`), with the exact message it must print, and
`./flow tool compiler/scripts/typecheck_rules.flow` runs them. The checker
is `compiler/src/sem_gpu.flow`.
