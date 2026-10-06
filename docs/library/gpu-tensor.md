# GPU tensors

Shaped, typed views of the same `GpuBuffer` resources used by ordinary `@gpu`
compute. The library is `stdlib/gpu_tensor.flow`. It does not add a second
inference runtime: model execution reads and writes that storage in place.

```flow
import "stdlib/gpu_tensor.flow"
import "stdlib/tensor.flow"

function main() -> i32 {
    let host: Tensor = tensor_fill(1, 4, 1, 1, 2.0)
    let x: GpuTensor = gpu_tensor_from_host(host)
    let y: GpuTensor = gpu_tensor_alloc_f32(1, 4, 1, 1)
    if gpu_tensor_require(x, GPU_DTYPE_F32, 1, 4, 1, 1) != 0 {
        return 1
    }
    if gpu_tensor_normalize(x, y, 2.0) != 0 {
        return 2
    }
    gpu_tensor_free(x)
    gpu_tensor_free(y)
    tensor_free(host)
    return 0
}
```

## Shared resources

| Path | When | Copy |
|------|------|------|
| `gpu_tensor_alloc` / `gpu_tensor_from_buffer` on unified memory | Metal shared buffers | Zero-copy: `gpu_tensor_ptr` is `gpu_host_ptr` |
| `gpu_tensor_from_host` / `gpu_tensor_to_host` | Always | Explicit upload / download |
| `gpu_tensor_view_host` | Backends that cannot alias host and device | Explicit host view, no `GpuBuffer` |
| Stub backend (`gpu_available()` is false) | Linux / Windows CI | Host staging with the same `GpuTensor` type |

`gpu_tensor_buffer` returns the `GpuBuffer` handle that GPU kernels
and compute passes consume. `gpu_tensor_ptr` is a CPU-visible mapping on
unified memory; calling an `@gpu`-annotated function through the C host path
is **not** automatically a multi-thread GPU dispatch. The Metal runtime
provides real device kernels for scale/bias, ReLU, clamp/invert and GEMM;
Flow's separate `./flow gpu` command emits the user-authored WGSL/Metal
kernels for supported GPU launchers.

## Compatibility

Shape, dtype, access and resource kind live on `GpuTensor` and on the
descriptor `GpuTensorLayout`. Checks do not need a device:

| Function | Role |
|----------|------|
| `gpu_tensor_require` | 0 if shape and dtype match; 1 empty, 2 dtype, 3 shape |
| `gpu_tensor_matches` / `gpu_tensor_compatible` | boolean shape+dtype tests |
| `gpu_tensor_can_bind` | dtype plus access bits (`READ`, `WRITE`, `READ_WRITE`) |
| `gpu_tensor_layout` / `gpu_tensor_layout_eq` | compare layouts without storage |

Closed dtype tags: `GPU_DTYPE_F32`, `GPU_DTYPE_F16`, `GPU_DTYPE_I32`,
`GPU_DTYPE_U8`. Resource kinds: `GPU_RES_BUFFER` (implemented) and
`GPU_RES_TEXTURE` (reserved for typed textures).

Model helpers (`gpu_tensor_linear`, `gpu_tensor_relu`, `gpu_tensor_normalize`)
refuse incompatible operands before they touch storage.

## vgpu model cases

`examples/gpu/vgpu/mnist.flow` and `examples/gpu/vgpu/depth_estimation.flow`
run a host-Tensor reference and a `GpuTensor` path over the same logical
buffers. On Metal's unified-memory backend, supported model operations use
real compute command buffers; the conformance result requires all expected
model dispatches to complete. On unsupported platforms the host numerical
fallback remains useful, but is reported as **UNSUPPORTED** for GPU parity.
The `@gpu` declarations separately emit backend shader source and are not
silently counted as device execution.

```bash
./flow run examples/gpu/vgpu/mnist.flow
./flow gpu examples/gpu/vgpu/mnist.flow
./flow gpu --wgsl examples/gpu/vgpu/mnist.flow
./flow gpu test --suite vgpu --all-backends
```

See [GPU Memory](gpu-memory.md) for the underlying `GpuBuffer` ABI and
[vgpu parity](../project/vgpu-parity.md) for the P3 resource model.

## WebGPU shared-resource multi-pass execution

`wasm/crossing_assets/gpu-multipass.mjs` exports
`runFlowGpuPasses(device, config)`. It consumes **Flow-emitted WGSL and
Flow compiler kernel reflection**, binds persistent `GPUBuffer` objects
once, submits any number of reflected compute stages in order, and only
reads back the explicitly requested final buffers. Per-stage parameters
use the same 16-byte-aligned uniform ABI as the existing
`webgpu-host.js` `runKernel` path.

The configuration names resources as a `Float32Array` (initial host
upload) or a positive element count (a device-only intermediate/result).
Each pass supplies the reflected `kernel`, its WGSL source,
`dispatchElements`, optional `bindings` mapping parameter names to
persistent resource names, optional `requiredElements` for shape
validation (especially matrix multiplication), and scalar uniforms.

The executor validates resource extents, workgroup limits,
read-before-write dependencies and same-pass alias hazards **before**
creating GPU objects. A real result has
`execution: "webgpu-device"` and `intermediateCpuCopies: 0`.
It cleans up created GPU objects when compilation or submission fails.

```bash
node --test tests/webgpu/multipass.test.mjs
```

The Node test uses a simulated WebGPU device to check two ordered kernels,
one queue submission, final-only readback, and error cleanup. It does
**not** prove MNIST/depth parity on a physical WebGPU adapter. The model
examples still need a compiler-to-browser launcher that carries their
actual generated WGSL, scalar reflection, weights and numerical
reference fixtures into this multi-pass executor.

