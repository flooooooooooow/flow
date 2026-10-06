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
**Metric:** Mean wall-clock runtime from repeated compiled-harness runs. The default is three runs per candidate, configurable with `--repetitions=N`. A fallback report is emitted when the LLVM toolchain is unavailable, and its selected schedule always comes from the supplied candidate set.

*(Note: The actual measured runtime metrics were skipped in this run due to missing LLVM dependencies in the execution VM, but the pipeline logic, simulation fallback, and code generation were fully verified).*

## Remaining Work
1. **Full Pipeline Integration:** The tuner is currently a schedule generator plus a measurement / search harness. It is not yet wired into the MLIR generator's primary execution path for suitable kernels (e.g., automatically tuning convolution and matrix multiplication loops during JIT compilation).
2. **Joint candidate representation:** Tile, vector, and unroll schedules are separate strategies. Search still explores a list of tile triples; a single individual that carries tile sizes, an unroll factor, and a vector width together is future work.
3. **Measured Bayesian surrogate:** The current Bayesian path is discrete inverse-distance UCB. A full Gaussian-process surrogate over measured runtimes, and an in-process `mlir-cpu-runner`, are still open.

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

## PMU feedback

The benchmark accepts an optional Linux `perf stat` event:

```bash
./flow tool benchmarks/micro/transform_tuning_benchmark.flow \
  --pmu-event=cache-misses
```

Supported events are `cycles`, `instructions`, `cache-misses`, `branches`,
`branch-misses`, `ipc`, `stalled-cycles-frontend`, and
`stalled-cycles-backend`. `ipc` is compared as cycles/instruction so every
metric stays a minimization. The benchmark keeps wall-clock timing when
`perf` is absent, the event is unavailable, or the kernel denies PMU access.
The selected metric is printed with the event name so reports remain
comparable across runs.

## Cost model and search

`--metric=cost-model` ranks candidates with an analytic reuse / cache /
remainder score and does not lower IR. `--search=genetic` and
`--search=bayesian` explore the supplied `--candidates` list instead of
evaluating every schedule. When the LLVM toolchain is missing, `--search`
uses the same cost model. `--print-cost` on `mlir_tune` prints the integer
score for one schedule.

See [MLIR Autotuning](../language/mlir-autotuning.md) for the command
surface.
