# GPU & Unified Memory

First-class device memory alongside CPU heap (`docs/library/memory.md`).

```flow
import "stdlib/gpu_memory.flow"
import "stdlib/memory.flow"

let gpu: GpuBuffer = gpu_alloc_f32(1024)
gpu_copy_h2d_f32(gpu, host, 1024 * 4)
gpu_copy_d2h_f32(host, gpu, 1024 * 4)
gpu_free(gpu)
```

Linked automatically by `./flow run` / `./flow debug`.

## Backends

| Platform | Backend | Notes |
|----------|---------|-------|
| macOS | **Metal** | Shared buffers = unified CPU/GPU (`gpu_host_ptr`) |
| Linux / Windows | **stub** | `gpu_available()` is false; alloc returns null |

## API

| Function | Role |
|----------|------|
| `gpu_available()` / `gpu_backend_name()` | Probe backend (`"metal"` / `"stub"`) |
| `gpu_alloc` / `gpu_alloc_unified` | Shared/unified buffer |
| `gpu_alloc_private` | Device-private (blit copies on Metal) |
| `gpu_alloc_f32` / `gpu_alloc_i32` / `gpu_alloc_f64` | Typed sizes |
| `gpu_free` | Release |
| `gpu_copy_h2d` / `gpu_copy_d2h` / `gpu_copy_d2d` | Transfers (`ptr<void>`) |
| `gpu_copy_h2d_i32` / `_f32` (+ d2h) | Typed convenience |
| `gpu_host_ptr` / `gpu_is_unified` | CPU mapping for shared buffers |
| `gpu_sync` | Wait for GPU work |
| `gpu_allocate` / `unified_allocate` / `gpu_copy_to_device` … | Aliases from older docs |

Flags: `GPU_MEM_DEFAULT`, `GPU_MEM_SHARED`, `GPU_MEM_PRIVATE`.

## Example

`examples/gpu/gpu_memory_roundtrip.flow` — H2D/D2H, unified map, private D2D.

## Runtime

- Header: `runtime/gpu_memory.h`
- Metal: `runtime/gpu_metal.m`
- Stub: `lib/runtime/gpu_memory_stub.flow` (non-Darwin; always-linked by `./flow`)
