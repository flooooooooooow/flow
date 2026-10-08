# Flow Benchmarks

Performance benchmarks for the Flow programming language.

## Published results

[RESULTS.md](RESULTS.md) holds the measured comparison of Flow against C,
Rust, and plain CPython: same algorithms, same sizes, same clang and flags
for Flow-generated C and hand-written C. Regenerate it with:

```bash
./flow tool bench_publish
```

The sources for those runs live in `publish/` with one directory per
language. The CPython sources live in `baselines/python/publish/`, with
the other Python benchmark subjects (see `baselines/python/README.md`).

## Structure

```
benchmarks/
├── publish/                  # Published cross-language comparison
│   ├── flow/                # Flow sources
│   ├── c/                   # Hand-written C equivalents
│   └── rust/                # Rust equivalents
├── baselines/python/        # CPython and NumPy subjects for every comparison
├── baselines/native/        # Hand-written C twins for native attribution
├── micro/                    # Micro-benchmarks
│   ├── fft_benchmark.flow   # Fast Fourier Transform
│   ├── ffi_boundary_benchmark.flow  # FFI scalar / batched / buffer timings
│   ├── mandelbrot_benchmark.flow  # Fractal computation
│   ├── matmul_benchmark.flow     # Matrix multiplication
│   ├── nbody_benchmark.flow      # N-body simulation
│   ├── parallel_scaling.flow     # Serial and disjoint-chunk parallel scaling
│   └── sort_benchmark.flow       # Sorting algorithms
└── runner.flow              # Benchmark runner with statistics
```

## Memory instrumentation

Runtime primitive attribution (#745) lives under
`baselines/native/cross_harness/runtime/`. Every runtime workload has a
hand-written C twin compiled with the same `clang -O3 -march=native -lm`
flags as generated Flow C. The harness records `flow_vs_python`,
`flow_vs_native` and `python_vs_native`. See
[docs/project/runtime-primitive-attribution.md](../docs/project/runtime-primitive-attribution.md).

```bash
./flow tool bench_harness --check-runtime-natives
./flow tool bench_harness --smoke --out /tmp/flow-runtime-attr.json
./flow tool bench_harness --eval-tax /tmp/flow-runtime-attr.json
```

`./flow tool bench_harness` sets `FLOW_MEM_PROFILE=1` on the memory suite
so runtime `flow_vs_native` ratios are not the #740 wrapper tax.
Compiled Flow programs then write heap count/bytes, peak live heap, peak
RSS, compiler-temp bytes and copy volume into the schema. No workload
source rewrite is required. See [docs/library/memory.md](../docs/library/memory.md).

## Running Benchmarks

### Individual Benchmarks

```bash
# Run the benchmark suite
./flow run benchmarks/runner.flow

# Run individual benchmarks
./flow run benchmarks/micro/sort_benchmark.flow
./flow run benchmarks/micro/matmul_benchmark.flow
./flow run benchmarks/micro/parallel_scaling.flow
```

### What Each Benchmark Measures

| Benchmark | Description | Key Metric |
|-----------|-------------|------------|
| `matmul` | Matrix multiplication (naive, tiled, unrolled) | GFLOPS |
| `mandelbrot` | Fractal computation (scalar, unrolled) | Mpixels/sec |
| `nbody` | N-body gravitational simulation | M interactions/sec |
| `fft` | Cooley-Tukey FFT | GFLOPS |
| `parallel_scaling` | Serial and disjoint-chunk parallel passes | Time (ms), efficiency |
| `sort` | Quicksort, heapsort, insertion sort | Time (ms) |
| `ffi_boundary_benchmark` | FFI boundary: pointer-identity row (copied_bytes=0) plus scalar / batched / large-buffer timings | Time (ms) |
| `ffi_breakeven` | Real C crossings (scalar, batch, zero-copy, copy, string, value, callback) and live `breakeven_batch=` | Batch size |
| `runtime_ffi_*` / `memory_ffi_*` | #728 harness rows for FFI boundary overhead and copy-byte instrumentation | Harness schema |

## Performance Targets

| Benchmark | Target vs C |
|-----------|-------------|
| Matrix Multiply | Within 2x |
| Mandelbrot | Within 1.5x |
| N-body | Within 2x |
| FFT | Within 2x |
| Sorting | Within 1.5x |

## Comparison Guide

To compare Flow against other languages:

### C
```bash
# Compile with optimizations
clang -O3 -march=native benchmark.c -o benchmark_c
./benchmark_c
```

### Julia
```julia
using BenchmarkTools
@btime your_function()
```

### Mojo
```bash
mojo run benchmark.mojo
```

## Adding New Benchmarks

1. Create a new `.flow` file in `micro/`
2. Follow the existing structure:
   - Include timing using `clock()`
   - Print results with clear formatting
   - Include verification where applicable
3. Add entry to this README

## Startup versus compile and run (#746)

`./flow tool bench_harness` writes a `timing_scope` field on every row of
its JSON output.

| Rows | Flow command | `timing_scope` |
|---|---|---|
| `cold_*`, `compiler_*` | `flow run --json file.flow` | `compile_and_execute` |
| `startup_hello`, `startup_tiny_arithmetic`, `startup_file_transform` | executable built before timing | `precompiled_exec_to_exit` |
| `runtime_*`, `memory_*` | executable built before timing | `precompiled_workload` |

The startup rows reuse the `cold` sources and Python twins, with no
warm-up. Their native C twins live in
`benchmarks/baselines/native/cross_harness/cold/` and are built with the
same clang flags as the generated Flow C. A cold row times compile and
execute, so it does not use them. `attribution.flow_vs_native` on a
startup row is what the Flow executable adds to process start over plain
C (loader, runtime initialization, linked libraries); 1.0 means nothing.
`--check-runtime-natives` fails when a startup program has no twin.

Startup rows measure wall time from process launch to exit, so they
include spawn cost and the program's own work. They are not an
`execve`-to-`main` measurement. The C twin pays the same spawn and exec
cost, and the ratio cancels it. On macOS the first run of a newly linked
binary also pays the system's code-signature check (about 200 ms). It
lands in the p95 and leaves the median alone. Compare rows only when the
CPU, the OS and the `timing_scope` match.

```bash
./flow tool bench_harness --smoke --out startup-smoke.json
./flow tool tests/bench_harness/run.flow
```
