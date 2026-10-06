# MLIR transform autotuning

The Flow-native tuner separates a structured kernel from the transform
schedule that tiles, vectorizes, interchanges, fuses, or unrolls it. Search
then picks a schedule with either measured runtime / PMU counts or an
analytic cost model.

## Schedule generator

```bash
./flow tool scripts/tools/mlir_tune/main.flow \
  --op=linalg.matmul --tiles=32,32,8 --target=cpu --strategy=tile
```

Accepted strategies are `tile`, `vector`, `interchange`, `fuse`,
`hierarchical_tile`, `hierarchical_vector`, and `unroll`. The module records
`flow.tune_target` and `flow.tune_strategy`. `--strategy=unroll` tiles first,
then unrolls the innermost loop:

```bash
./flow tool scripts/tools/mlir_tune/main.flow \
  --strategy=unroll --tiles=32,32,8 --unroll-factor=4
```

`--unroll-factor` is an integer from 2 through 16. The generated module also
records `flow.tune_unroll_factor`.

`--print-cost` writes the integer cost-model score of `--tiles` for
`--extent` (default 128) and `--target` instead of a transform module. Lower
is better. GPU-family targets (`gpu`, `nvptx`, `amdgpu`) prefer larger tiles.

## Measurement harness

```bash
./flow tool benchmarks/micro/transform_tuning_benchmark.flow \
  --candidates=8,8,8;16,16,8;32,16,8;64,32,16
```

The default metric is compiled-harness wall time when `mlir-opt`,
`mlir-translate`, and a C compiler are present. `--metric=cost-model` ranks
the same candidates with the analytic model and does not lower IR.

`--search=genetic` and `--search=bayesian` explore the candidate space
instead of evaluating every schedule. `--evals=N` (1–64) is the evaluation
budget. `--seed=N` makes the genetic path deterministic.

```bash
./flow tool benchmarks/micro/transform_tuning_benchmark.flow \
  --search=bayesian --metric=cost-model \
  --candidates=8,8,8;16,16,8;32,16,8;64,32,16 --evals=4 --seed=1
```

Bayesian search uses inverse-distance interpolation and a lower-confidence
bound over the discrete tile space. Genetic search uses tournament
selection, per-dimension crossover, and mutation snapped back onto the
supplied candidates. When the LLVM toolchain is missing, `--search`
falls back to the cost model.

## PMU events

`--pmu-event` accepts `cycles`, `instructions`, `cache-misses`, `branches`,
`branch-misses`, `ipc`, `stalled-cycles-frontend`, and
`stalled-cycles-backend`. `ipc` is compared as cycles/instruction (CPI) so
every metric stays a minimization. Wall time remains the fallback when
`perf` or the counter is unavailable. `--metric=cost-model` cannot be
combined with a PMU event.

The pass-pipeline flags used after a schedule is chosen are documented in
[MLIR Opt Flags](mlir-opt-flags.md). The project report for issue #668 is
`docs/project/MLIR_AUTOTUNING.md`.
