# GPU & Unified Memory

First-class device memory alongside CPU memory. The library is `stdlib/gpu_memory.flow`; host allocation helpers live in `stdlib/memory.flow`.

```flow
import "stdlib/gpu_memory.flow"
import "stdlib/memory.flow"

function main() -> i32 {
    if !gpu_available() {
        return 0
    }

    let n: i64 = 8
    let bytes: i64 = n * 4
    let host: ptr<i32> = alloc_i32(n)
    let out: ptr<i32> = alloc_i32(n)
    if host == null or out == null {
        return 1
    }

    let gpu: GpuBuffer = gpu_alloc_i32(n)
    if gpu_is_null(gpu) {
        free(host)
        free(out)
        return 1
    }

    let h2d: i32 = gpu_copy_h2d_i32(gpu, host, bytes)
    let d2h: i32 = gpu_copy_d2h_i32(out, gpu, bytes)
    gpu_sync()

    gpu_free(gpu)
    free(host)
    free(out)

    if h2d != 0 or d2h != 0 {
        return 1
    }
    return 0
}
```

Linked automatically by `flow run` / `flow debug`.

## Backends

| Platform | Backend | Notes |
|----------|---------|-------|
| macOS | Metal | shared buffers expose unified CPU/GPU storage |
| Linux / Windows | stub | `gpu_available()` is false; allocation returns null |

## API

| Function | Role |
|----------|------|
| `gpu_available()` / `gpu_backend_name()` | probe backend |
| `gpu_alloc` / `gpu_alloc_unified` | shared/unified buffer |
| `gpu_alloc_private` | device-private storage |
| `gpu_alloc_f32` / `gpu_alloc_i32` / `gpu_alloc_f64` | typed allocation |
| `gpu_free` | release |
| `gpu_copy_h2d` / `gpu_copy_d2h` / `gpu_copy_d2d` | raw transfers |
| typed H2D/D2H helpers | typed convenience transfers |
| `gpu_host_ptr` / `gpu_is_unified` | CPU mapping for shared buffers |
| `gpu_sync` | wait for GPU work |

Flags include `GPU_MEM_DEFAULT`, `GPU_MEM_SHARED`, and `GPU_MEM_PRIVATE`.

The full checked round-trip is [`examples/gpu/gpu_memory_roundtrip.flow`](../../examples/gpu/gpu_memory_roundtrip.flow).

Runtime implementation: `runtime/gpu_memory.h`, `runtime/gpu_metal.m`, and `runtime/gpu_memory_stub.c`.

## Buffer-size and dispatch safety

The Flow wrappers reject these calls before they reach the GPU backend:

- a copy larger than the source or destination buffer's `size`;
- an allocation with unknown flags, or a typed allocation whose count is
  zero, negative or overflows the byte size;
- an f32 kernel whose count exceeds any of its three buffers or the
  shader's 32-bit count.

A rejected copy or kernel returns `-1`; a rejected allocation returns a
null buffer. `GpuBuffer.size` is a public field, so the Metal runtime
checks the native allocation sizes again before it dispatches.

Shared-to-shared device copies use `memmove`, so overlapping buffers copy
correctly.
