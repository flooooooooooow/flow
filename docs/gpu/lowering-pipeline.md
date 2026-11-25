# GPU lowering pipeline

`flow gpu-lower` takes the `@gpu` functions of a Flow program through the
MLIR gpu dialect to each GPU target: SPIR-V for Vulkan, Metal Shading
Language and a Metal library, an MLX kernel, NVIDIA PTX and a cubin, and an
AMDGPU code object. With `--run` it runs the kernels where this machine
can and compares every result buffer with the CPU build of the same
program.

The driver is `tools/flow_cli/gpu_lower.flow`. The passes are in
`tools/flow_cli/gpu_passes.flow`, which `flow mlir-spirv` also uses. The
host runners are `tools/gpu_lower/vk_run.c` (Vulkan) and
`tools/gpu_lower/metal_run.m` (Metal).

## Command

```text
./flow gpu-lower PROGRAM.flow [--target T] [-o OUT] [--run] [--ulp N]
                 [--chip SM] [--amd-chip GFX] [--sdk SDK]
```

| Target | Artefact | Checked with | Runs here |
|---|---|---|---|
| `spirv` (default) | `.spv` | `spirv-val --target-env vulkan1.0` | Vulkan through MoltenVK |
| `msl` | `.metal` | `xcrun metal` when run | Metal |
| `metal` | `.metallib` | `xcrun metal`, `xcrun metallib` | Metal |
| `mlx` | `_mlx.py` | MLX compiles the kernel when run | MLX |
| `ptx` | `.ptx` | a second PTX from `llc`, and the entry points | no |
| `cubin` | `.cubin` | `ptxas` | no |
| `hsaco` | `.hsaco` | the kernel descriptors in the ELF symbols | no |
| `all` | every one of the above | | |

The artefacts go to `build/gpu-lower/STEM/` unless `-o` names a file.
With `all`, a target whose tools are missing is skipped with a note.

Status 0. 1 when a step fails or a result is out of tolerance. 2 for
usage. 3 when a tool, or the hardware for `--run`, is missing.

## The kernel module

`flow flow-to-mlir --gpu` writes the host program with one `gpu.module
@flow_kernels` that holds a `gpu.func ... kernel` per `@gpu` function. The
pipeline first moves that gpu.module into a module of its own with
`gpu.container_module`, and replaces `gpu.block_dim` with the workgroup
size the emitter gives every kernel, 64 x 1 x 1 (its
`spirv.entry_point_abi`). The SPIR-V lowering would fold `gpu.block_dim`
to that size anyway. The AMDGPU lowering otherwise calls
`__ockl_get_local_size` from the ROCm device library.

A launch is a count of workgroups of 64 x 1 x 1 threads in x, y and z.

## Passes per target

All MLIR passes run in `mlir-opt` from LLVM 22.

### SPIR-V

```text
builtin.module(
  gpu.module(scf-for-to-while),
  spirv-attach-target{ver=v1.0 caps=Shader exts=SPV_KHR_storage_buffer_storage_class},
  convert-gpu-to-spirv,
  spirv.module(spirv-lower-abi-attrs, spirv-update-vce))
```

The `spirv.module` alone then goes through `mlir-translate
--no-implicit-module --serialize-spirv`, and the binary through
`spirv-val --target-env vulkan1.0`.

Each kernel argument is a storage buffer in descriptor set 0, binding I for
argument I. A scalar argument is a one-element buffer.

`scf-for-to-while` works around a bug in `convert-gpu-to-spirv`. It lowers
an `scf.for` result through a Function variable that is stored only inside
the loop body, so a loop that runs zero times leaves its result undefined.
Without the pass, thread 0 of `tests/gpu_lower/kernels/zero_trip.flow`
returned 0.0 on MoltenVK where the CPU returns 3.5. The `scf.while`
lowering carries the values through the loop header.

### Metal Shading Language and Metal

```text
spirv-cross KERNELS.spv --msl --msl-decoration-binding --entry NAME --stage comp
xcrun -sdk macosx metal -fno-fast-math -c KERNELS.metal -o KERNELS.air
xcrun -sdk macosx metallib KERNELS.air -o KERNELS.metallib
```

SPIRV-Cross writes one entry point per run, so it runs once per kernel and
the files are joined with each struct and constant kept once. With
`--msl-decoration-binding`, argument I is `[[buffer(I)]]`.

### MLX

The `mlx` target writes a Python script. Each kernel's MSL becomes the
`header` of an `mx.fast.metal_kernel`, with the kernel function turned
into a plain function that the kernel body calls. An argument the kernel
stores to is an MLX output, which starts at zero. Every other argument is
an input. MLX places an input of fewer than 8 elements in the `constant`
address space, so the script picks the address space per argument. The
script refuses a kernel that writes a buffer whose starting contents are
not zero.

```text
build/mlx-venv/bin/python -I build/gpu-lower/STEM/STEM_mlx.py DATA_DIR OUT_DIR
```

`$FLOW_MLX_PYTHON` names the Python. The default is
`build/mlx-venv/bin/python`, made with:

```text
python3 -m venv build/mlx-venv
build/mlx-venv/bin/pip install mlx numpy
```

### PTX and cubin

```text
--gpu-lower-to-nvvm-pipeline=cubin-chip=sm_80 cubin-features=+ptx70 cubin-format=isa
```

`mlir-opt --dump-pass-pipeline` expands it to:

```text
builtin.module(
  convert-nvgpu-to-nvvm, gpu-kernel-outlining, convert-vector-to-scf,
  convert-scf-to-cf, convert-nvvm-to-llvm, convert-func-to-llvm,
  expand-strided-metadata,
  nvvm-attach-target{O=2 chip=sm_80 features=+ptx70 triple=nvptx64-nvidia-cuda},
  lower-affine, convert-arith-to-llvm, convert-index-to-llvm{index-bitwidth=64},
  canonicalize, cse,
  gpu.module(convert-gpu-to-nvvm{index-bitwidth=64}),
  gpu.module(canonicalize), gpu.module(cse),
  gpu.module(reconcile-unrealized-casts),
  gpu-to-llvm, gpu-module-to-binary{format=isa},
  convert-math-to-llvm, canonicalize, cse, reconcile-unrealized-casts)
```

The PTX is the `assembly` string of the `gpu.binary` it leaves. `--chip`
picks the SM.

The PTX is checked twice. Each kernel must be a `.visible .entry` with the
parameters of the MLIR memref calling convention: five per 1-D memref
(allocated and aligned pointer, offset, size, stride) and one per scalar.
The same pipeline with `cubin-format=llvm` gives the NVVM IR, which `llc
-mtriple=nvptx64-nvidia-cuda` turns into a second PTX; the two must match
instruction for instruction. LLVM has no PTX assembler, so nothing here
assembles the PTX.

`--target cubin` uses `cubin-format=bin`, which runs `ptxas`. Without
`ptxas` on `PATH` it stops with status 3.

### AMDGPU code object

```text
builtin.module(
  rocdl-attach-target{chip=gfx90a},
  convert-scf-to-cf,
  gpu.module(convert-gpu-to-rocdl{chipset=gfx90a}),
  reconcile-unrealized-casts)
```

`gpu-module-to-binary` would link the ROCm device libraries from
`/opt/rocm`. Instead, the gpu.module body becomes an LLVM module with its
data layout and the `amdgcn-amd-amdhsa` triple, then:

```text
mlir-translate --mlir-to-llvmir
llc -O3 -mtriple=amdgcn-amd-amdhsa -mcpu=gfx90a -filetype=obj
ld.lld -shared
```

The step fails if the LLVM IR calls anything other than an `llvm.*`
intrinsic. The check is that the ELF has a `NAME.kd` kernel descriptor for
every kernel. `--amd-chip` picks the target.

## Execution parity

`--run` builds the program for the CPU with flowc and runs it with
`$FLOW_GPU_LOWER_DATA` set to a directory. The program's `main()` runs
each kernel once per thread id, through its own `gpu_thread_id()`, and
writes:

| File | Contents |
|---|---|
| `launch.txt` | `buffer IDX f32\|i32 COUNT ROLE` lines, then `dispatch KERNEL GX GY GZ IDX...` lines |
| `in_IDX.bin` | each buffer before the first dispatch |
| `out_IDX.bin` | each result buffer after the CPU run |

The GPU run starts from the `in_IDX.bin` files and runs the dispatches in
order. Every `out_IDX.bin` is then compared with the GPU's buffer. An i32
buffer must match exactly. An f32 buffer must be within `--ulp` units in
the last place, 0 by default, which is bit for bit. The programs in
`tests/gpu_lower/kernels/` are written this way.

The CPU build is `clang -O2 -ffp-model=strict -ffp-contract=on`, or
`$FLOW_GPU_LOWER_CC` with `$FLOW_GPU_LOWER_CFLAGS`. The two options decide
whether bit for bit is possible:

- The Metal compiler fuses `a * b + c` into one fused multiply-add.
  `-ffp-contract=on` makes clang do the same within an expression. With
  `-ffp-contract=off`, saxpy differed in 198 of 1000 elements, by up to
  122 ulp where `a * x` and `y` nearly cancel.
- flowc marks a reduction loop `#pragma clang loop vectorize(enable)`, and
  under that pragma clang reorders the additions. `-ffp-model=strict`
  keeps them in source order, as the GPU adds them. At plain `-O2`, 49 of
  the 64 partial sums of `reduce.flow` differed, by up to 18 ulp, and the
  total by 1 ulp.

### Results

Apple M4 Max, macOS 26.2, Homebrew LLVM 22.1.7, MoltenVK 1.4.0 (Vulkan
1.4.323), SPIRV-Cross 1.4.363, MLX 0.32.4.

| Program | Kernel | Vulkan | Metal | MLX |
|---|---|---|---|---|
| `saxpy.flow` | `out = a * x + y`, 1000 elements | 1000/1000 bit-identical | 1000/1000 | 1000/1000 |
| `reduce.flow` | sum of 4096 values: 64 partial sums, then a total | 64/64 and 1/1 | 64/64 and 1/1 | 64/64 and 1/1 |
| `stencil2d.flow` | one heat-equation step on 96 x 40, 2D launch | 3840/3840 | 3840/3840 | 3840/3840 |
| `lj_forces.flow` | Lennard-Jones forces, 200 particles in 3D, all pairs | 600/600 | 600/600 | 600/600 |
| `zero_trip.flow` | prefix sums, thread 0's loop runs zero times | 64/64 | 64/64 | 64/64 |
| `modal_bank.flow` | 128 stateful resonators, two 64-sample blocks, SoA state + mix | pending device re-measure | pending | pending |
| `voice_filters.flow` | 128 one-pole + biquad voices, two 64-sample blocks, 1- and 2-float SoA state + mix | 12/12 buffers bit-identical | 12/12 | pending (no MLX here) |
| `voice_osc_varblocks.flow` | 64 phase oscillators, 48 then 80 frames, mid-stream freq/gain update | pending device re-measure | pending | pending |
| `ks_delay.flow` | 64 Karplus-Strong voices, 48-sample ring per voice, dynamic read index + write-index state, two 64-sample blocks | 6/6 buffers bit-identical | 6/6 | pending (no MLX here) |
| `remainder.flow` | integer `%`: a stride-3 ring wrap and negative dividends and divisor, 64 threads | pending device re-measure | pending | pending |

`modal_bank.flow` is registered in `tests/gpu_lower/cases.txt` at 0 ulp and
is covered by the CPU cross-block harness plus PTX/HSACO generation checks.
Its device bit-identical cells above stay pending until re-measured on the
same Apple Silicon host as the original five; do not treat generation PASS
or SKIP as a substitute for those cells.

`voice_filters.flow` adds the one-pole and biquad voice programs from the
GPU audio epic's correctness gate, with one-float and two-float per-voice
state respectively, carried across two 64-sample dispatches. Its Vulkan and
Metal cells were measured on the reference host above (Apple M4 Max, macOS
26.2) at 0 ulp; MLX was not measured because no MLX environment was present.
It is recorded at 0 ulp in `tests/gpu_lower/cases.txt`, and its CPU
cross-block checks run in CI without a GPU.

`voice_osc_varblocks.flow` extends the audio correctness gate beyond the
fixed-length modal bank: a different voice program (phase accumulator),
unequal block lengths (48 then 80), and new SoA frequency/gain buffers on
the second dispatch. Its CPU harness fails if phase is reset between
blocks, if block 1 is replayed at the old length or coefficients, or if
the first sample of block 1 matches a reset-from-init formula. Registered
at 0 ulp in `tests/gpu_lower/cases.txt`; device cells above stay pending
until re-measured on the reference host.

`ks_delay.flow` is the Karplus-Strong voice program. Each voice keeps a
48-sample ring in device memory and its own write index, reads the ring at a
dynamic index, and wraps that index with compare-and-assign, so the kernel
needs a local assigned inside an `if` inside a `for`. Two 64-sample blocks
run back to back and the second dispatch reads the state the first one left,
while an independent unsplit replay of voice 0 checks every sample, the
mid-block ring contents and the continuation formula. Vulkan and Metal were
bit-identical on the reference host; MLX was not measured here. The construct
it relies on is why the kernel `if` emitter now carries assigned locals out
of the `scf.if` (#1765).

`remainder.flow` checks integer `%` in a kernel (#1770): `(idx[t] + 3) % n`
for a ring index advanced by more than one, plus a negative dividend and a
negative divisor, where the result must keep the dividend's sign as the
host's truncating remainder does. Its CPU build checks every thread against
`l - (l / r) * r` and hand-computed values. It was 64/64 bit-identical on all
three buffers through Mesa lavapipe (Vulkan on the CPU, Linux x86-64);
the reference-host cells above stay pending until measured there.

Every established case above is bit for bit, so `tests/gpu_lower/cases.txt`
sets a tolerance of 0 ulp for all of them. `msl` runs the same MSL as
`metal` and gives the same results. PTX, the cubin and the code object were
not run: there is no NVIDIA or AMD GPU here.

### Tests

```text
./flow tool tests/gpu_lower/run.flow [--require T,T,...] [--only PROGRAM]
```

The runner lowers every program in `tests/gpu_lower/cases.txt` to every
target, runs the runnable ones with `--run`, and reports PASS, SKIP (a
tool or the hardware is missing) or FAIL. A target named in `--require`
fails where it would skip. On this Mac, `--require spirv,metal,mlx,ptx,hsaco`
passes.

It then checks that a broken kernel fails. It runs the first program again
with `FLOW_GPU_LOWER_MUTATE=addf-subf`, which turns the kernel's first
`arith.addf` into `arith.subf` before lowering, and requires exit status 1
and a FAIL line. For saxpy that run reports 0/1000 bit-identical.

The CPU build and the GPU kernel come from the same source, so the check
finds faults in lowering, code generation and the runtimes. A kernel that
is wrong in its source is wrong on both sides and passes.

## Known gaps

- The `@gpu` emitter in `compiler/src/mlirgen.flow` accepts thread and
  block ids, `+ - * /`, integer `%`, comparisons, `if`, counted `for`
  loops, loads, stores and `gpu_barrier()`. Integer `%` is the host's
  truncating remainder (the sign follows the dividend), lowered to
  `arith.remsi` on signed scalars (#1770); float and unsigned `%` are
  refused by name. It has no casts, no `and` or `or`, no math
  functions such as `sqrt`, and no workgroup memory. A local assigned
  inside an `if` is not merged after it. The test kernels stay inside this
  subset: the Lennard-Jones kernel needs no `sqrt`, and splits its pair
  loop at `i` to skip the self pair without a branch.
- The workgroup size is fixed at 64 x 1 x 1.
- The cubin path has not run, because `ptxas` is not installed here.
- PTX and the AMDGPU code object are generated and checked but have not
  run. A host that launches the PTX must pass each memref as the five
  descriptor fields and use blocks of 64 threads.
- An MLX output starts at zero, so the MLX target cannot run a kernel that
  updates a buffer in place.
- Three differences between flowc's C backend and the gpu dialect turned
  up while writing the tests. The test kernels write their types and put
  float constants in typed locals to avoid them:
  - an unannotated `let v = p[i]` with `p: ptr<f32>` is `int32_t` in C;
  - a float literal next to an f32 operand is a C `double`, where the gpu
    dialect keeps it f32;
  - the `vectorize(enable)` pragma on reductions lets clang reorder float
    additions.
