# Baseline benchmarks

This directory contains independent performance baselines.

- `numeric.flow`: Dense matrix multiply (300x300 doubles)
- `string_io.flow`: String concatenation loop (50000 times)
- `startup.flow`: Startup time overhead
- `./flow tool bench_baselines`: Benchmark runner (the Flow program in `scripts/tools/bench_baselines`)
