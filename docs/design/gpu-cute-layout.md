# CuTe-style GPU layout algebra for Flow (research proposal)

Status: **research / design candidate**, not a shipped CUDA backend or a
stable language/API contract. The executable P0 proof is
[`examples/gpu/cute_layout_reference.flow`](../../examples/gpu/cute_layout_reference.flow).

Upstream reference: NVIDIA CUTLASS 4.7.0
[CuTe DSL introduction](https://docs.nvidia.com/cutlass/4.7.0/media/docs/pythonDSL/cute_dsl_general/dsl_introduction.html),
[Layout algebra](https://docs.nvidia.com/cutlass/4.7.0/media/docs/cpp/cute/02_layout_algebra.html),
and [static/dynamic layouts](https://docs.nvidia.com/cutlass/4.7.0/media/docs/pythonDSL/cute_dsl_general/dsl_dynamic_layout.html).

## Why this belongs in Flow

CuTe's critical abstraction is not merely JIT or a GPU decorator. A **layout
is a coordinate-to-index map**, built from hierarchical shape/stride tuples.
The algebra composes, divides, complements, inverts and coalesces these maps,
making the mapping from logical tensor elements to threads, warps, blocks and
memory explicit. Then a compiler can specialize a kernel for that mapping.

Flow already supports `@gpu`, Metal and WGSL output
(`compiler/src/sem_gpu.flow`, `metal_codegen.flow`,
`wgsl_codegen.flow`). `lib/stdlib/gpu_tensor.flow` owns typed tensor
buffers and basic shape metadata. This is **not** CuTe-equivalent: the
`GpuTensorLayout` descriptor has dimensions but no strides, nested modes,
thread-value decomposition, swizzle, or layout algebra. There is no claimed
production CUDA/PTX backend.

The target design is:

```text
Flow kernel + tensor/layout expressions
            |
     semantic layout algebra
     [logical tensor coordinates -> storage/thread coordinates]
            |
     validated typed IR + specialization/cache
            |
     tile/partition/fusion/schedule selection
            |
   +--------+------------+------------+
 CUDA/NVVM/PTX       Metal         WGSL
   |                    |             |
 NVIDIA GPU          Apple GPU     WebGPU
```

**One semantic layout language, with target-specific legality and lowering.**
Tensor Cores, NVIDIA asynchronous memory copies, and thread-block clusters
must be CUDA-specific lowerings, not fake shared features on all devices.

## P0: semantic executable (included)

`examples/gpu/cute_layout_reference.flow` implements ordinary Flow
functions for **rank-2 affine layout evaluation**, transpose, conservative
row-major coalescing, generic *evaluated* composition, grid/tile partitioning,
and partial-tile validity. No device or Python dependency.

A layout `L` with positive logical shape `(M, N)`, nonnegative strides
`(sM, sN)`, and origin `o` maps:

```text
L(i, j) = o + i * sM + j * sN
```

`L(2,3) = 19` for shape `(4,8)` and strides `(8,1)`.
Transposition swaps shape/stride axes without moving data. Zero strides
represent broadcast. For an arbitrary selector `B`, evaluated composition
is `(A o B)(i) = A(B(i))`, where `B(i)` is interpreted as a flattened
logical coordinate in `A`, **not** an assumed affine output layout.

Given tile `(TM,TN)`, grid `(ceil(M/TM), ceil(N/TN))` and local
coordinates `(u,v)`, the mapping is:

```text
tile(tr, tc, u, v) = L(tr*TM + u, tc*TN + v)
```

Out-of-range coordinates return -1, including masked edges; physical
offsets are computed in i64 after validating nonnegative i32 shapes and
strides. The P0 proof intentionally does **not** implement CuTe's full
hierarchical tuple algebra, swizzle or layout-closure rules. In particular
the P0 coalescer accepts only a contiguous row-major flattening that fits
i32; it must not be mistaken for CuTe's general `coalesce`.

Run the reference with:

```sh
./flow run examples/gpu/cute_layout_reference.flow
```

Expected on successful execution:

```text
cute_layout_reference: PASS
```

Its `main` returns distinct nonzero codes when row/column-major offsets,
transpose, coalesce, noncontiguous composition, zero-stride broadcast,
ragged tiles, or bounds checks fail. This is a testable reference,
**not a performance benchmark**.

## P1: real hierarchical layout algebra

Make a representation independent of buffer ownership. Represent a nested
`IntTuple` of shapes/strides and distinguish (a) the logical domain,
(b) the physical storage index, and (c) the thread/value distribution. A
static tuple must be available at compile time; shape and stride may be
dynamic where the backend supports them.

Define and test exact semantics for `composition`, `coalesce`,
`complement`, `logical_divide`, `logical_product`, `right_inverse`
and `left_inverse`. The tests must compare coordinate-to-index maps against
the CuTe reference over small exhaustive domains and reject layouts that
violate assumptions. For swizzles and hierarchical modes, never silently
approximate the mapping with plain affine strides.

Decide the public API, names, static/dynamic type rules, invalid-layout
diagnostics, and ownership/lifetime behavior **before** shipping syntax.
Record outstanding decisions in `docs/project/Questions.md`; don't make
`@gpu` silently change meaning.

## P2: GPU tile and copy semantics

Extend the IR to distinguish tensor storage spaces (global, shared,
register/tensor memory), thread layouts, vectorization and alignment.
Partition logical layouts across lane/warp/block, then map tile copies
through an explicit copy plan. Add resource bounds, alignment, synchronization,
race and alias checks. Backend capability must be explicit: an illegal
device operation is a compile error or a reported unsupported result, not
an invisible CPU fallback.

Prove correctness first on Metal and WGSL for regular and ragged tile
shapes. An unchanged reference layout test must run on CPU-only CI.

## P3: actual CUDA backend

Introduce CUDA target detection and a CUDA lowering pipeline (e.g. MLIR
GPU/NVVM to PTX where supported), runtime loading/launching, memory
transfers, synchronization, stream semantics and architecture-specific
feature flags. Prove a simple vector add and GEMM numerically **on a real
NVIDIA device** before claiming CUDA support.

Only then add CuTe-like MMA/copy atoms, warpgroup pipelines, TMA, shared
memory staging and the relevant SM90/SM100 specializations where legal.
Metal's SIMD-group matrix instructions are separate lowering choices.
Never claim Tensor Core usage from compilation or a host-reference result
alone: verify executed kernels on device.

## P4: specialization, fusion, autotuning and parity

Cache compiled kernels by target architecture, signature, layout, static
arguments and compiler version; dynamic arguments must not be incorrectly
baked into cached kernels. Connect layout transformations to the existing
Flow MLIR optimizer and fusion work. Benchmark coherent variants against
baseline Flow `@gpu` and NVIDIA CuTe DSL using the **same** shapes,
dtypes, tolerance, batch sizes, cold/warm cache state and real GPU hardware.
Include correctness, compile time, launch time and steady-state bandwidth/
FLOP/s. Until these measurements exist, no throughput or speedup claim
is supported.

## Integration invariants

Keep `GpuBuffer` as storage ownership; a layout is a non-owning view/mapping.
Do not store ambiguous physical-stride meaning in current
`GpuTensorLayout` without a versioned contract. Do not change
`compiler/src/` in an exploratory PR, since it triggers self-hosted
bootstrap regeneration and broad parity gates. Backend-specific functions
must not leak into target-neutral layout algebra. Preserve portable
CPU-only semantic tests when native GPU hardware is unavailable.

P0 is a narrow reference proving the *need and semantics*. It is **not**
CuTe DSL compatibility, a GPU backend, compiler lowering, or an optimized
GEMM implementation.
