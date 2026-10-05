# Baseline benchmarks

This directory contains independent performance baselines.

- `numeric.flow`: Dense matrix multiply (300x300 doubles)
- `string_io.flow`: String concatenation loop (50000 times)
- `startup.flow`: Startup time overhead
- `./flow tool bench_baselines`: Benchmark runner (the Flow program in `scripts/tools/bench_baselines`)

Cross-harness text/I/O rows for #747 live under `benchmarks/cross_harness`
(`runtime/string_concat`, `runtime/parse_format`, `runtime/buffered_io`,
`cold/file_transform`) with CPython twins in `python/cross_harness`. Run them
with `./flow tool bench_harness --smoke`.
