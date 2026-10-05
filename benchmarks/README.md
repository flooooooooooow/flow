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

`./flow tool bench_harness` sets `FLOW_MEM_PROFILE=1` on every subject.
Compiled Flow programs then write heap count/bytes, peak live heap, peak
RSS, compiler-temp bytes and copy volume into the schema (issue #740).
No workload source rewrite is required. See [docs/library/memory.md](../docs/library/memory.md).

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
