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

`gpu_tensor_buffer` returns the `GpuBuffer` handle that `@gpu` kernels, compute
passes and (once typed textures land) storage-texture binds consume. Pre- and
post-model `@gpu` kernels take `gpu_tensor_ptr` of that same resource.

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
buffers, with `@gpu` preprocess and postprocess kernels on those pointers.
Both backends emit from the same source:

```bash
./flow run examples/gpu/vgpu/mnist.flow
./flow gpu examples/gpu/vgpu/mnist.flow
./flow gpu --wgsl examples/gpu/vgpu/mnist.flow
./flow gpu test --suite vgpu --all-backends
```

See [GPU Memory](gpu-memory.md) for the underlying `GpuBuffer` ABI and
[vgpu parity](../project/vgpu-parity.md) for the P3 resource model.

## Device execution and verification

On a supported Metal device, `gpu_tensor_normalize`,
`gpu_tensor_scale_bias`, `gpu_tensor_relu`,
`gpu_tensor_invert01` and `gpu_tensor_linear` now dispatch Metal
compute pipelines directly over the shared `GpuBuffer` handles.
Operations use a host fallback only when no native device kernel path is selected; once selected, any GPU dispatch error propagates instead of silently producing a CPU result. Unsupported private-storage copies stay explicit, and
private-storage copies remain explicit. The Metal GEMM uses a simple
one-thread-per-output kernel (correctness-first, **not** a tuned matmul).

`gpu_model_dispatch_count()` is a completed-device-dispatch counter.
The model examples emit `GPU_DEVICE_EXECUTED metal` only when at least
one actual Metal compute command completed during the example. The vgpu
numerical runner additionally requires the program's CPU-reference
comparison to pass. For WebGPU it runs the example's `@gpu` kernels on a
real adapter through Deno and compares the readback with the example's
host reference (see [vgpu conformance](../gpu/vgpu-conformance.md#numerical-cases)).
On hosts with no device it reports `UNSUPPORTED reason=device-execution`
rather than claiming GPU parity from shader emission or the CPU reference.

The examples are deterministic *MNIST-shaped* and *depth-shaped*
computations, not accuracy measurements on the real MNIST test corpus
or a depth-estimation model benchmark. Running the upstream vgpu models
needs their captured weights and inputs and a frozen output to compare
against.
