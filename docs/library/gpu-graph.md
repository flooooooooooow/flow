# GPU render/compute graph

Backend-independent IR for multi-pass GPU programs. The library is
`stdlib/gpu_graph.flow`. It is the P2 resource/pass model from
[vgpu-parity.md](../project/vgpu-parity.md): storage buffers, storage
textures, ping-pong pairs, transient resources, dispatch dimensions,
workgroup memory, barriers, and hazard checks.

Sampled textures, samplers, vertex/index buffers, typed render targets
and vertex/fragment stage declarations belong to the typed-resource
surface (issue #811). This module does not define those types. Bind them
later by the same integer resource id. Storage textures live here because
the graph has to name read/write access and a format tag to check
hazards.

```flow
import "stdlib/gpu_graph.flow"

function main() -> i32 {
    let mut g: GpuGraph = gpu_graph_vgpu_fluid()
    let err: GpuGraphError = gpu_graph_validate(&g)
    if err.code != GPU_GRAPH_OK {
        return 1
    }
    # Same Flow graph lowers to both backends.
    let wgsl: string = gpu_graph_emit_wgsl_pass(g, 0)
    let metal: string = gpu_graph_emit_metal_pass(g, 0)
    if wgsl == "" or metal == "" {
        return 2
    }
    return 0
}
```

`gpu frame { ... }` remains a parse-only host syntax hook. Programs build
the graph with ordinary Flow calls so #811 types can plug in by id
without a second IR.

## Resources

| Kind | Constructor | Notes |
|---|---|---|
| Storage buffer | `gpu_graph_add_storage_buffer` | `array<f32>` in WGSL, `device float*` in Metal |
| Storage texture | `gpu_graph_add_storage_texture` | format tag + 1D/2D/3D; not a sampled `gpu.texture` |

Access is `GPU_GRAPH_ACCESS_READ`, `GPU_GRAPH_ACCESS_WRITE` or `GPU_GRAPH_ACCESS_READ_WRITE`.
Lifetime is `GPU_LIFE_PERSISTENT` or `GPU_LIFE_TRANSIENT`. A transient
resource must be written before it is read.

Format tags (`GPU_GRAPH_FMT_R32FLOAT`, `RG32FLOAT`, `RGBA16FLOAT`,
`RGBA8UNORM`) are integers so a later typed-format enum can share them.

## Passes and ping-pong

`gpu_graph_add_compute` records workgroup size, dispatch size, workgroup
shared bytes and a barrier flag. `gpu_graph_add_render` records a draw
count and resource bindings only. Geometry types stay on the #811
surface.

`gpu_graph_add_pingpong` pairs two distinct physical resources.
`gpu_graph_bind_pingpong` snapshots the current front/back into the pass;
`gpu_graph_pingpong_swap` flips the pair for later binds. Binding the
same physical resource as both sides is rejected at construction.

A Jacobi loop records its iteration count with `gpu_graph_set_iterations`.
The executors run that many dispatches and bind the other side of each
ping-pong pair on odd iterations.

## Hazard checks

`gpu_graph_validate` rejects, before any backend emit:

| Code | Meaning |
|---|---|
| `GPU_GRAPH_ERR_CONFLICTING_BINDING` | two bindings share a slot |
| `GPU_GRAPH_ERR_SAME_PASS_RW` | same physical resource is read and written in one pass |
| `GPU_GRAPH_ERR_PINGPONG_ALIAS` | ping-pong pair names one physical resource |
| `GPU_GRAPH_ERR_BAD_ACCESS` | binding access exceeds the resource declaration |
| `GPU_GRAPH_ERR_WORKGROUP` | workgroup threads or shared bytes exceed backend limits (256 / 16 KiB) |
| `GPU_GRAPH_ERR_BARRIER` | shared memory without a workgroup barrier |
| `GPU_GRAPH_ERR_TRANSIENT` | transient read before write |
| `GPU_GRAPH_ERR_UNKNOWN_RESOURCE` | binding names a missing id |

Same-pass read/write is allowed only with an explicit supported mode:
`gpu_graph_set_feedback` on that pass, or
`gpu_graph_set_hazard_mode(g, GPU_HAZARD_ALLOW_FEEDBACK)` on the graph.

On success the function derives dependency edges from typed access: a
later pass that reads or writes a physical resource a earlier pass wrote
(or a later write after an earlier read) becomes an edge. Edges are not
duplicated host wiring: `gpu_graph_has_dep` reads what validation
recorded.


## Backends

`gpu_graph_emit_wgsl_pass` and `gpu_graph_emit_metal_pass` emit one pass
from the same graph: storage bindings, workgroup size, stage input and the
shader body. The bodies for the fluid and ocean passes live in
`lib/stdlib/gpu_graph_kernels.flow`. An unknown kernel gives an empty
result. `gpu_graph_same_source_both_backends` checks that every pass
produces code for both backends.

The inverse transform is a direct DFT, O(n²) per row and column, written for
correctness. A Stockham butterfly kernel would be faster. The spectrum is
deterministic synthetic data.

Two executors run the emitted code on a device: the native executor below
(Metal) and the browser host (WebGPU). Both take the same graph, accept the
same raw initial bytes per resource, and return the render pass as
`rgba8unorm` pixels.

## vgpu families

| Builder | Upstream | Passes |
|---|---|---|
| `gpu_graph_vgpu_fluid` | [fluid](https://vgpu.sh/examples/fluid) | splat velocity, splat dye, advect, curl, vorticity, divergence, pressure×20, project, advect-dye, display |
| `gpu_graph_vgpu_fft_ocean` | [fft-ocean](https://vgpu.sh/examples/fft-ocean) | deterministic spectrum, evolve, row/column inverse DFT, finalize, normals/foam, present |
| `gpu_graph_vgpu_fft_ocean_surface` | [fft ocean surface](https://vgpu.sh/examples/fft-ocean-surface) | same compute graph, `surface` present pass |

The two splat passes stand in for vgpu's pointer input. Every frame a fixed
jet at (0.25, 0.5) adds velocity (220, 50) and orange dye with a Gaussian
falloff, so a run from zeroed resources shows dye. Each ping-pong pair
swaps an even number of times per frame, so the next frame reads the side
the last one wrote.

```bash
./flow run examples/gpu/vgpu/fluid.flow
./flow run examples/gpu/vgpu/fft_ocean.flow
./flow run examples/gpu/vgpu/graph_device.flow
```

## Native executor

`stdlib/gpu_graph_exec.flow` runs a graph on the host GPU. On macOS the
backend is `runtime/gpu_metal_graph.m`. On other hosts
`gpu_graph_exec_new` returns `GPU_GRAPH_EXEC_ERR_UNAVAILABLE`.

```flow
import "stdlib/gpu_graph_exec.flow"

extern {
    function malloc(size: i64) -> ptr<void>
}

function main() -> i32 {
    let mut g: GpuGraph = gpu_graph_vgpu_fluid()
    let mut ex: GpuGraphExec = gpu_graph_exec_new(&g)
    if ex.code != GPU_GRAPH_EXEC_OK {
        println(ex.message)
        return 0
    }
    let run: GpuGraphRun = gpu_graph_exec_run(&ex, 64, 64)
    let px: ptr<u8> = malloc(64 * 64 * 4) as ptr<u8>
    let rc: i32 = gpu_graph_exec_readback(&ex, px, 64 * 64 * 4)
    println(run.execution)
    println(run.compute_dispatches)
    gpu_graph_exec_free(&ex)
    return rc
}
```

| Function | Does |
|---|---|
| `gpu_graph_exec_available()` | true when a native backend and a device exist |
| `gpu_graph_exec_new(g)` | validates, allocates every physical resource zero-filled, compiles one pipeline per pass |
| `gpu_graph_exec_upload(ex, id, src, n)` | replaces a resource with raw bytes in its layout |
| `gpu_graph_exec_run(ex, w, h)` | runs every pass once and renders a `w`×`h` frame |
| `gpu_graph_exec_readback(ex, dst, n)` | copies the last frame, `w * h * 4` bytes, top row first |
| `gpu_graph_exec_read_resource(ex, id, dst, n)` | copies a resource's raw bytes |
| `gpu_graph_resource_byte_size(g, id)` | the byte count an upload or read of `id` uses |
| `gpu_graph_exec_free(ex)` | releases the device resources |

Raw layouts match the WebGPU host's `initialResources`: `f32` for a
storage buffer, and row-major texels for a 2D storage texture (4 bytes for
`r32float` and `rgba8unorm`, 8 for `rg32float` and `rgba16float`).

A run records every pass, in the order the graph lists them, into one
command buffer. Validation only derives forward edges, so that order is a
topological order of the dependencies. Compute passes share one concurrent
compute encoder. A memory barrier goes before each dispatch that has a
derived dependency on an earlier pass, and before every iteration after
the first. Odd iterations bind the other side of each ping-pong pair. The
render pass draws a fullscreen triangle into an `rgba8unorm` target, which
is copied to a shared buffer before the command buffer is committed. The
run waits for completion. `GpuGraphRun` reports dispatches, barriers,
render passes, completed frames and GPU time, and `execution` is
`"metal-device"`.

Resources persist across runs, so a second `gpu_graph_exec_run` advances a
simulation by one frame. Shaders compile with fast math off.

The executor refuses, with `GPU_GRAPH_EXEC_ERR_UNSUPPORTED`, graphs it
cannot run as written: feedback passes or the feedback hazard mode,
workgroup memory, 1D or 3D textures, physical aliases, a pass without a
Metal body, and graphs without exactly one render pass. An invalid graph
gives `GPU_GRAPH_EXEC_ERR_INVALID`. Compilation, allocation and submission
failures give `GPU_GRAPH_EXEC_ERR_BACKEND` with the Metal message. Bad ids,
byte counts and sizes give `GPU_GRAPH_EXEC_ERR_ARGUMENT`.

## CPU reference

`stdlib/gpu_graph_reference.flow` evaluates the same graph on the CPU.
`gpu_graph_reference_run(g, w, h, frames, out)` runs `frames` frames from
zeroed resources with the executors' rules: recorded pass order, ping-pong
iterations, stores rounded to the texture format (`rgba16float` to half
precision, ties to even), and a render pass sampled at pixel centres. Each
kernel in `gpu_graph_kernels.flow` has a scalar twin. A pass without one
gives `GPU_GRAPH_REF_ERR_KERNEL`.

It is the oracle for the device runs. Device `exp`, `sin` and `cos` differ
from the C library in the last bits, so compare with a tolerance.

## Browser WebGPU graph execution

`lib/stdlib/gpu_graph_export.flow` validates the graph, then exports
resource and alias descriptors, ping-pong pairs, ordered passes, dispatch
dimensions, binding slots, iterations, dependencies and the WGSL generated
from the same graph as JSON.

`wasm/crossing_assets/gpu-graph-host.mjs` (mirrored under
`site/wasm-crossings/gpu/`) consumes that JSON. It allocates the resources,
builds an explicit bind group layout for each pass from its typed bindings,
dispatches compute passes in order, swaps ping-pong bindings for repeated
iterations, renders the fullscreen final stage and returns an `rgba8unorm`
readback. The layout comes from the graph, so a binding the shader does
not read keeps its slot. The fluid display pass binds velocity and reads
only dye.

Generated WGSL that fails device compilation, a missing storage-texture
language feature, invalid aliases, oversized dispatches, and unsupported
feedback or shared-memory passes are errors, never success verdicts.

```sh
mkdir -p build
./flow run examples/gpu/vgpu/export_fluid_graph.flow > build/fluid-graph.json
./flow run examples/gpu/vgpu/export_ocean_graph.flow > build/ocean-graph.json
```

In a browser with WebGPU, from a secure context:

```js
import { runFlowWebGpuGraph } from "./gpu-graph-host.mjs";
const adapter = await navigator.gpu.requestAdapter();
if (!navigator.gpu.wgslLanguageFeatures.has(
    "readonly_and_readwrite_storage_textures")) {
  throw new Error("browser cannot read Flow storage textures");
}
const device = await adapter.requestDevice();
const graph = await (await fetch("/build/fluid-graph.json")).json();
const run = await runFlowWebGpuGraph(device, graph, {width:64,height:64});
console.log(run.execution, run.computeDispatches, run.rgba);
```

Chrome ships the `readonly_and_readwrite_storage_textures` language
feature. Deno 2.7 accepts the shaders but does not advertise the feature,
so a Deno run has to add it to `navigator.gpu.wgslLanguageFeatures` and
drop the `requires` line from each pass first.

The host contract has mock-device coverage:

```sh
node --test tests/webgpu/graph-host.test.mjs
```

## Device results

One frame at 64×64 from zeroed resources, compared per `rgba8unorm` channel
with the CPU reference. Apple M4 Max, macOS, 2026-10-08.

| Graph | Backend | Dispatches | Max error vs reference | Channels that differ | Max error vs Metal |
|---|---|---|---|---|---|
| fluid | Metal (native executor) | 28 | 1 | 15 | |
| fluid | WebGPU, Chrome 154 headless | 28 | 1 | 15 | 0 |
| fluid | WebGPU, Deno 2.7 with the feature shim | 28 | 1 | 15 | 0 |
| fft_ocean | Metal | 6 | 1 | 1 | |
| fft_ocean | WebGPU, Chrome 154 | 6 | 1 | 1 | 0 |
| fft_ocean | WebGPU, Deno 2.7 | 6 | 1 | 1 | 0 |
| fft_ocean_surface | Metal | 6 | 1 | 1 | |
| fft_ocean_surface | WebGPU, Chrome 154 | 6 | 1 | 1 | 0 |
| fft_ocean_surface | WebGPU, Deno 2.7 | 6 | 1 | 1 | 0 |

`examples/gpu/vgpu/graph_device.flow` prints the Metal rows, with a
tolerance of 2. `tests/runtime/test_gpu_graph_exec.flow` checks the same
on any host with a Metal device.

## Limits

The reference is the Flow graph's own math. Captured vgpu.sh frames are no
fixed target for these graphs: the upstream fluid is driven by pointer
input, and the upstream ocean uses a random Phillips spectrum and an FFT.

Advection is nearest-neighbour: it rounds a backtrace offset to a whole
cell. A last-bit difference near a half-cell boundary moves a texel, and
the error grows with frames. After 3 frames the fluid differs from the
reference by up to 29 in a few channels, and after 10 frames by 255 in
481 channels. Single frames agree within 1.
