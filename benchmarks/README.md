# Flow Benchmarks

Performance benchmarks for the Flow programming language.

## Structure

```
benchmarks/
├── micro/                    # Micro-benchmarks
│   ├── fft_benchmark.flow   # Fast Fourier Transform
│   ├── mandelbrot_benchmark.flow  # Fractal computation
│   ├── matmul_benchmark.flow     # Matrix multiplication
│   ├── nbody_benchmark.flow      # N-body simulation
│   └── sort_benchmark.flow       # Sorting algorithms
└── runner.flow              # Benchmark runner with statistics
```

## Running Benchmarks

### Individual Benchmarks

```bash
# Run the benchmark suite
./flow run benchmarks/runner.flow

# Run individual benchmarks
./flow run benchmarks/micro/sort_benchmark.flow
./flow run benchmarks/micro/matmul_benchmark.flow
```

### What Each Benchmark Measures

| Benchmark | Description | Key Metric |
|-----------|-------------|------------|
| `matmul` | Matrix multiplication (naive, tiled, unrolled) | GFLOPS |
| `mandelbrot` | Fractal computation (scalar, unrolled) | Mpixels/sec |
| `nbody` | N-body gravitational simulation | M interactions/sec |
| `fft` | Cooley-Tukey FFT | GFLOPS |
| `sort` | Quicksort, heapsort, insertion sort | Time (ms) |

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
