# MLIR Auto-tuning Report (Issue #668)

## Overview
This report documents the initial integration of an MLIR transform dialect auto-tuner , first in the Python host (`src/flow/mlir_optimizer.py`, now retired) and now in `benchmarks/micro/transform_tuning_benchmark.flow` (`./flow tool benchmarks/micro/transform_tuning_benchmark.flow`). The auto-tuner attempts to find the best parameter (e.g., tile size) for a given kernel by generating multiple instances of the kernel's optimization pipeline, lowering them to LLVM IR, executing them via a test harness, and measuring actual runtime performance.

## Tuning Harness & Benchmark
A new microbenchmark was added at `benchmarks/micro/transform_tuning_benchmark.flow`. This program sets up a `linalg.matmul` kernel and evaluates several tile sizes through mlir-opt's transform interpreter. 

If the environment is fully equipped with the required toolchain (`mlir-opt`, `mlir-translate`, and `clang`), the auto-tuner drives the compilation and runs a small C-harness to measure the raw execution time of each tiled kernel.

### Initial Tuning Results
**Tuned Parameter:** Three-dimensional tile schedule for `linalg.matmul`.
**Evaluated Schedules:** [8,8,8], [16,16,8], [32,16,8], [64,32,16]
**Best Schedule:** Selected from measured runtime when the LLVM toolchain is available.
**Metric:** Wall-clock runtime from the compiled harness. A fallback report is emitted when the LLVM toolchain is unavailable.

*(Note: The actual measured runtime metrics were skipped in this run due to missing LLVM dependencies in the execution VM, but the pipeline logic, simulation fallback, and code generation were fully verified).*

## Remaining Work
1. **Full Pipeline Integration:** The tuner is currently exposed as a utility method. It needs to be wired directly into the MLIR generator's primary execution path for suitable kernels (e.g., automatically tuning convolution and matrix multiplication loops during JIT compilation).
2. **Toolchain Dependency Resolution:** The evaluation loop needs a dependable fall-back or an integrated `mlir-cpu-runner`. It currently shells out to `clang` and `mlir-translate`, which might not be present on all host systems.
3. **Parameter Expansion:** The benchmark now evaluates multi-dimensional `tile_sizes [M, N, K]` schedules. Future work can add vector and unroll parameters to the same candidate representation.

## Target metadata

Transform schedules carry an explicit target so measurements remain tied to the
backend that produced them:

```bash
./flow tool scripts/tools/mlir_tune/main.flow \
  --target=nvptx --op=linalg.matmul --tiles=64,64,16
```

Accepted targets are `cpu`, `gpu`, `nvptx`, and `amdgpu`. The generated module
records `flow.tune_target` and `flow.tune_strategy`. Candidate measurements can
therefore be grouped by target before a schedule is selected.
