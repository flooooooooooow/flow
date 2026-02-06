# Flow Language Benchmark Suite

Accurate, cross-language performance comparison between Flow, C, and Python.

## Quick Start

```bash
cd benchmarks/suite
./run_benchmarks.sh           # Run all benchmarks
./run_benchmarks.sh fibonacci # Run single benchmark
```

## The 4 Benchmarks

### 1. Fibonacci (Naive Recursive)
**What it tests:** Function call overhead, recursion

Computes `fib(N)` using the naive recursive algorithm: `fib(n) = fib(n-1) + fib(n-2)`. This is intentionally not optimized to measure raw function call performance.

| Metric | N=35 | N=40 |
|--------|------|------|
| Call depth | ~9.2M | ~102M |
| Complexity | O(2^n) | O(2^n) |

### 2. N-Body Simulation
**What it tests:** Floating-point arithmetic, struct access, memory patterns

Simulates the gravitational interactions of the solar system (Sun + 4 planets) using the standard N-body algorithm from the Computer Language Benchmarks Game.

| Metric | Value |
|--------|-------|
| Bodies | 5 (solar system) |
| Time step | 0.01 |
| Algorithm | O(N²) pairwise forces |

### 3. Matrix Multiplication
**What it tests:** Loop performance, cache efficiency, FLOPS

Computes C = A × B for NxN matrices using both naive and cache-friendly (transposed B) algorithms.

| Size | Operations | Peak GFLOPS (theoretical) |
|------|------------|---------------------------|
| 128×128 | 4.2M | ~10 |
| 256×256 | 33.5M | ~10 |
| 512×512 | 268M | ~10 |
| 1024×1024 | 2.1B | ~10 |

### 4. Spectral Norm
**What it tests:** Floating-point precision, power iteration

Computes the largest eigenvalue of an infinite matrix using 10 iterations of power method. From the Computer Language Benchmarks Game.

| Size | Matrix elements | Iterations |
|------|-----------------|------------|
| 5500 | ~30M | 10 |

## Methodology

### Compilation Flags

All compiled languages use the same optimization level:

```bash
# C
clang -O3 -march=native -ffast-math

# Flow (generates C, then compiled with same flags)
flow compile file.flow  # generates C
clang -O3 -march=native -ffast-math generated.c
```

### Timing

- **C/Flow:** Uses `clock()` for CPU time
- **Python:** Uses `time.perf_counter()` for wall-clock time

### Fair Comparison Rules

1. **Same algorithm** - Identical logic across all implementations
2. **Same data types** - f64/double throughout for floating-point
3. **Same optimizations** - No language-specific tricks
4. **Same problem sizes** - Identical N values where possible

## Expected Results

On a typical modern machine (M1/M2 Mac, Intel i7, AMD Ryzen):

| Benchmark | C | Flow | Python | Flow/C Ratio |
|-----------|---|------|--------|--------------|
| Fibonacci (N=40) | 0.17s | 0.17s | 14s | ~1.0x |
| N-Body (50M steps) | 2.1s | 2.1s | N/A* | ~1.0x |
| Matrix (1024) | 1.8s | 1.8s | 150s | ~1.0x |
| Spectral (5500) | 2.0s | 2.0s | 45s | ~1.0x |

*Python is too slow for large N-body runs; uses 1M iterations instead.

## Why These Benchmarks?

| Benchmark | Real-world application |
|-----------|------------------------|
| Fibonacci | Compiler optimization, recursion limits |
| N-Body | Physics simulation, games, scientific computing |
| Matrix Multiply | Machine learning, graphics, linear algebra |
| Spectral Norm | Eigenvalue problems, stability analysis |

## Adding New Benchmarks

1. Create implementations in `flow/`, `c/`, `python/`
2. Follow naming: `NN_name.{flow,c,py}`
3. Include timing and result verification
4. Update `run_benchmarks.sh`

## Interpreting Results

### Flow vs C

Flow compiles to C, so performance should be nearly identical (within 5%). Differences may come from:
- Slightly different generated code patterns
- Type coercion overhead
- Function call conventions

### C vs Python

Expect 50-100x speedup for C/Flow over Python on these benchmarks. Python's interpreted nature and dynamic typing add significant overhead.

## References

- [Computer Language Benchmarks Game](https://benchmarksgame-team.pages.debian.net/benchmarksgame/)
- [N-body problem](https://en.wikipedia.org/wiki/N-body_simulation)
- [Spectral norm](https://en.wikipedia.org/wiki/Spectral_radius)
