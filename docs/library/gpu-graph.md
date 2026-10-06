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
    let mut g: GpuGraph = gpu_graph_new()
    let source: i32 = gpu_graph_add_storage_buffer(&g, "src",
        GPU_ACCESS_READ, GPU_LIFE_PERSISTENT, 64)
    let dest: i32 = gpu_graph_add_storage_buffer(&g, "dst",
        GPU_ACCESS_WRITE, GPU_LIFE_PERSISTENT, 64)
    let copy: i32 = gpu_graph_add_copy_f32(&g, "copy", source, dest)
    if copy < 0 or gpu_graph_validate(&g).code != GPU_GRAPH_OK {
        return 1
    }
    if not gpu_graph_same_source_both_backends(g) {
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

Access is `GPU_ACCESS_READ`, `GPU_ACCESS_WRITE` or `GPU_ACCESS_READ_WRITE`.
Lifetime is `GPU_LIFE_PERSISTENT` or `GPU_LIFE_TRANSIENT`. A transient
resource must be written before it is read.

Format tags (`GPU_GRAPH_FMT_R32FLOAT`, `RG32FLOAT`, `RGBA16FLOAT`,
`RGBA8UNORM`) are integers so a later typed-format enum can share them.

## Passes and ping-pong

`gpu_graph_add_compute` records workgroup size, dispatch size, workgroup
shared bytes and a barrier flag. `gpu_graph_add_render` records a draw
count and resource bindings only — geometry types stay on the #811
surface.

`gpu_graph_add_pingpong` pairs two distinct physical resources.
`gpu_graph_bind_pingpong` snapshots the current front/back into the pass;
`gpu_graph_pingpong_swap` flips the pair for later binds. Binding the
same physical resource as both sides is rejected at construction.

A Jacobi or Stockham loop is one pass with `gpu_graph_set_iterations`,
not an unrolled list of identical nodes.

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
duplicated host wiring — `gpu_graph_has_dep` reads what validation
recorded.

## Backends

`gpu_graph_add_copy_f32` constructs a *real* backend-neutral buffer
copy operation with checked source/destination capacities and distinct
resources. `gpu_graph_emit_wgsl_pass` and `gpu_graph_emit_metal_pass`
lower it into actual indexed assignments with bounds checks and shader
entry-point declarations. The WGSL buffer destination uses the required
`read_write` storage access (WGSL has no write-only storage-buffer mode).

**No-op shaders do not count as execution.** A structural
`gpu_graph_add_compute` or `gpu_graph_add_render` pass that has not yet
been assigned a supported numerical operation returns an empty shader
string, and `gpu_graph_same_source_both_backends` is false. In particular,
the fluid and FFT-ocean builders currently validate hazard graphs but
still lack their numerical body, dispatch wiring and image comparison.
Their examples and `flow gpu test --suite vgpu` report `UNSUPPORTED`,
not parity. Actual device execution and readback remain acceptance work
for #812.


## Actual WebGPU device execution: reflected f32 copy

The executable `gpu_graph_add_copy_f32` operation emits BOTH the
WGSL compute entry and JSON binding reflection from the same typed Flow
graph. That reflection plugs into the existing
`wasm/crossing_assets/webgpu-host.js` `runKernel` API. The
`runFlowGraphCopy` adapter verifies exact f32 readback bits: successful
shader compilation alone cannot produce an `execution: "webgpu-device"`
result.

Produce both browser artifacts from Flow source:

```sh
./flow run examples/gpu/vgpu/copy_graph.flow
node tools/gpu_graph/export_copy.mjs
python3 -m http.server 8000 --directory site
```

Open `http://localhost:8000/wasm-crossings/gpu/copy-graph.html` in a
WebGPU-enabled browser and select **Execute on GPU**. That page fetches
the WGSL and reflection emitted by Flow, creates a real compute
pipeline, dispatches the kernel, maps a readback buffer and checks the
result against the source. It does not embed an alternative handwritten
WGSL implementation.

Regression commands:

```sh
./flow run tests/lang/test_gpu_graph.flow
node --test tests/webgpu/graph-copy.test.mjs
```

The Node test uses a mock GPU device to exercise the dispatch/readback
host interface and failure paths; it does **not** establish Metal/WebGPU
hardware parity on its own. True #812 completion still requires fluid,
FFT-ocean, air-painting and radiance-cascade algorithms, actual device
submissions on both targets, and reference-output validation.

## vgpu families

| Builder | Upstream | Passes |
|---|---|---|
| `gpu_graph_vgpu_fluid` | [fluid](https://vgpu.sh/examples/fluid) | advect, curl, vorticity, divergence, pressure×20, project, advect-dye, display |
| `gpu_graph_vgpu_fft_ocean` | [fft-ocean](https://vgpu.sh/examples/fft-ocean) | initial spectrum, evolve, Stockham IFFT, finalize, normals/foam, present |
| `gpu_graph_vgpu_fft_ocean_surface` | [fft ocean surface](https://vgpu.sh/examples/fft-ocean-surface) | same compute graph, `surface` present pass |

```bash
./flow run examples/gpu/vgpu/fluid.flow
./flow run examples/gpu/vgpu/fft_ocean.flow
```
