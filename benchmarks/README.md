# FLOW Performance Benchmarks

This directory contains comprehensive performance benchmarks comparing FLOW against C implementations on both CPU and GPU.

## Benchmark Suite

### CPU Benchmarks
- **Matrix Multiplication** (512x512): Dense matrix multiplication
- **Sorting Algorithms**: Bubble sort and quick sort (10,000 elements)
- **Vector Operations**: Addition and multiplication (1M elements)
- **Fibonacci**: Recursive and iterative implementations (n=40)
- **Prime Counting**: Count primes up to 1,000,000
- **Monte Carlo Pi**: 10M samples for Pi estimation

### GPU Benchmarks
- **Matrix Multiplication**: Parallel matrix multiplication
- **Vector Operations**: Parallel vector addition and multiplication

## Files

- `c_benchmarks.c` - C reference implementations with high-resolution timing
- `flow_benchmarks.flow` - FLOW implementations of all benchmarks
- `main.flow` - Main FLOW benchmark runner
- `run_benchmarks.py` - Python script to compile and run both suites
- `benchmark_results.json` - Results output (generated after running)

## Running Benchmarks

### Quick Start
```bash
cd benchmarks
python run_benchmarks.py
```

### Options
```bash
python run_benchmarks.py --help
python run_benchmarks.py --cleanup    # Clean temp files after
python run_benchmarks.py --c-only     # Run only C benchmarks
python run_benchmarks.py --flow-only  # Run only FLOW benchmarks
```

### Manual Compilation

#### C Benchmarks
```bash
clang -O3 -march=native -lm -lrt c_benchmarks.c -o c_benchmarks
./c_benchmarks
```

#### FLOW Benchmarks
```bash
cd ..  # Back to root
python run_bench.py benchmarks/main.flow
```

## Expected Output

The benchmark runner will:
1. Compile both C and FLOW implementations with optimizations
2. Run all benchmarks and collect timing data
3. Display a comparison table with speedup ratios
4. Save detailed results to `benchmark_results.json`

Example output:
```
🏁 PERFORMANCE COMPARISON RESULTS
================================================================================
Benchmark                           C Time (s)   FLOW Time (s)   Speedup  
---------------------------------------------------------------------------
Matrix Multiplication CPU          0.123456     0.098765        1.25x
Vector Addition CPU               0.002345     0.001987        1.18x
...
OVERALL                           2.345678     1.987654        1.18x
```

## Performance Notes

- C is compiled with `-O3 -march=native` for maximum optimization
- FLOW uses MLIR JIT compilation with similar optimization levels
- GPU benchmarks use Metal on Apple Silicon (simulated for now)
- All timings use high-resolution monotonic clocks
- Results may vary based on hardware and thermal state

## Interpreting Results

- **Speedup > 1.0**: FLOW is faster than C
- **Speedup < 1.0**: C is faster than FLOW
- **Speedup ≈ 1.0**: Performance is comparable

GPU benchmarks will show additional parallel speedup compared to CPU versions.

## Troubleshooting

1. **Compilation fails**: Ensure clang and Python dependencies are installed
2. **Metal errors**: GPU benchmarks require macOS with Metal support
3. **Timeout errors**: Increase timeout in `run_benchmarks.py` for slower hardware
4. **Inconsistent results**: Run multiple times and average for stable measurements
