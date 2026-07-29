# Flow benchmark results

Date: 2026-07-29

Flow compiles to C. The comparison that matters is Flow against
hand-written C built by the same clang with the same flags. Rust and
plain CPython run the same algorithms at the same sizes for context.

## Summary

| Benchmark | Flow median (s) | C median (s) | Rust median (s) | Python median (s) | Flow / C |
|---|---|---|---|---|---|
| fib | 0.0161 | 0.0158 | 0.0171 | 1.2663 | 1.02x |
| nbody | 0.0320 | 0.0257 | 0.0217 | 5.4521 | 1.24x |
| matmul | 0.0167 | 0.0167 | 0.0197 | 2.3087 | 1.00x |
| spectral | 0.0093 | 0.0110 | 0.0060 | 1.4208 | 0.85x |
| mandelbrot | 0.0069 | 0.0069 | 0.0085 | 0.5317 | 1.00x |

Flow / C below 1.00x means the Flow binary was faster on that run.
Differences within a few percent are run-to-run noise.

## Notes

- nbody is the one benchmark where the Flow binary trails hand C by
  more than noise. The arithmetic in the generated C is identical.
  The hand-written C declares its functions static, which lets clang
  specialize the pair loop for the constant body count at the call
  site. Flow emits externally visible functions, which blocks that
  specialization. Two manual experiments support this: adding static
  to the generated functions moved Flow into C's range, and removing
  static from the hand C moved C into Flow's range.

## Benchmarks

### fib

Naive recursive Fibonacci, fib(35). Function call overhead.

| Language | Median (s) | Min (s) | Max (s) | Result |
|---|---|---|---|---|
| Flow | 0.0161 | 0.0154 | 0.0203 | 9227465 |
| C | 0.0158 | 0.0155 | 0.0161 | 9227465 |
| Rust | 0.0171 | 0.0167 | 0.0174 | 9227465 |
| Python | 1.2663 | 1.2446 | 1.3009 | 9227465 |

### nbody

Outer solar system, 5 bodies, 1,000,000 steps (Benchmarks Game).

| Language | Median (s) | Min (s) | Max (s) | Result |
|---|---|---|---|---|
| Flow | 0.0320 | 0.0319 | 0.0324 | -0.169086185 |
| C | 0.0257 | 0.0257 | 0.0264 | -0.169086185 |
| Rust | 0.0217 | 0.0214 | 0.0219 | -0.169086185 |
| Python | 5.4521 | 5.3365 | 6.4218 | -0.169086185 |

### matmul

Dense matrix multiply, naive triple loop, 300x300 doubles.

| Language | Median (s) | Min (s) | Max (s) | Result |
|---|---|---|---|---|
| Flow | 0.0167 | 0.0165 | 0.0171 | 202497.750000 |
| C | 0.0167 | 0.0167 | 0.0168 | 202497.750000 |
| Rust | 0.0197 | 0.0182 | 0.0206 | 202497.750000 |
| Python | 2.3087 | 2.2025 | 3.6507 | 202497.750000 |

### spectral

Spectral norm, N=500, 10 power iterations (Benchmarks Game).

| Language | Median (s) | Min (s) | Max (s) | Result |
|---|---|---|---|---|
| Flow | 0.0093 | 0.0090 | 0.0101 | 1.274224116 |
| C | 0.0110 | 0.0088 | 0.0135 | 1.274224116 |
| Rust | 0.0060 | 0.0058 | 0.0065 | 1.274224116 |
| Python | 1.4208 | 1.4114 | 1.4883 | 1.274224116 |

### mandelbrot

Mandelbrot membership count, 400x400 grid, 100 iterations.

| Language | Median (s) | Min (s) | Max (s) | Result |
|---|---|---|---|---|
| Flow | 0.0069 | 0.0068 | 0.0070 | 39687 |
| C | 0.0069 | 0.0068 | 0.0070 | 39687 |
| Rust | 0.0085 | 0.0084 | 0.0086 | 39687 |
| Python | 0.5317 | 0.5285 | 0.5540 | 39687 |

## Compile time

Measured once per benchmark. Compile time is excluded from every
workload number.

| Benchmark | Flow transpile (s) | clang on generated C (s) | clang on hand C (s) | rustc (s) |
|---|---|---|---|---|
| fib | 0.09 | 0.05 | 0.04 | 0.09 |
| nbody | 0.09 | 0.06 | 0.09 | 0.12 |
| matmul | 0.09 | 0.05 | 0.05 | 0.11 |
| spectral | 0.09 | 0.06 | 0.05 | 0.11 |
| mandelbrot | 0.09 | 0.05 | 0.05 | 0.09 |

## Method

- Each program times only its workload with a monotonic clock and
  prints the elapsed seconds itself. Compiler time, transpile time,
  and process startup are excluded.
- One warmup run, then 5 timed repetitions per program.
  Median, min, and max of the timed repetitions are reported.
- Identical algorithms, data sizes, and double precision floats in
  every language. Sources live in benchmarks/publish/.
- Flow-generated C and hand-written C are compiled by the same
  clang with the same flags: `-O3 -march=native`.
  `-ffast-math` is not used.
- Rust: `rustc -C opt-level=3 -C target-cpu=native`, one source file per
  benchmark, compiled directly with rustc.
- Python is plain CPython without numpy.
- Result values are printed by every program and checked for
  agreement across languages before this report is written.
- The machine was otherwise idle.

## Environment

- CPU: Apple M4 Max, 14 cores, 36 GB RAM
- C compiler: Apple clang version 17.0.0 (clang-1700.6.3.2)
- Python: Python 3.9.6
- Rust: rustc 1.92.0 (ded5c06cf 2025-12-08)

## Reproduce

```bash
./benchmarks/run_publish.sh
```

This regenerates benchmarks/RESULTS.md in place. A full run takes
a few minutes; most of that is the Python repetitions.
