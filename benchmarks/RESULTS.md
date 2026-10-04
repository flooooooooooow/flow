# Flow benchmark results

Date: 2026-10-03

Flow compiles to C. The comparison that matters is Flow against
hand-written C built by the same clang with the same flags. Rust and
plain CPython run the same algorithms at the same sizes for context.

## Summary

| Benchmark | Flow median (s) | C median (s) | Rust median (s) | Python median (s) | Flow / C |
|---|---|---|---|---|---|
| fib | 0.0372 | 0.0373 | 0.0376 | 2.1813 | 1.00x |
| nbody | 0.0866 | 0.0760 | 0.0574 | 10.0939 | 1.14x |
| matmul | 0.0403 | 0.0426 | 0.0409 | 7.7846 | 0.95x |
| spectral | 0.0159 | 0.0158 | 0.0162 | 3.9735 | 1.00x |
| mandelbrot | 0.0190 | 0.0191 | 0.0313 | 0.9356 | 0.99x |

Flow / C below 1.00x means the Flow binary was faster on that run.
Differences within a few percent are run-to-run noise.

## Notes on Epic #727

- **Flow beats CPython** broadly across the suite. This meets the core epic bar.
- **Flow trails hand-written C** on `nbody` by a noticeable margin.
  - **Cause**: Flow emits externally visible functions, preventing clang from specializing the pair loop for the constant body count at the call site (which the hand-written C can do via static).
  - **Tracker**: This gap points at sub-issue #739/#751 (scalar inner loops) and #740 for resolution.

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
| Flow | 0.0372 | 0.0372 | 0.0375 | 9227465 |
| C | 0.0373 | 0.0372 | 0.0374 | 9227465 |
| Rust | 0.0376 | 0.0375 | 0.0384 | 9227465 |
| Python | 2.1813 | 2.1688 | 2.2271 | 9227465 |

### nbody

Outer solar system, 5 bodies, 1,000,000 steps (Benchmarks Game).

| Language | Median (s) | Min (s) | Max (s) | Result |
|---|---|---|---|---|
| Flow | 0.0866 | 0.0832 | 0.1081 | -0.169086185 |
| C | 0.0760 | 0.0754 | 0.0775 | -0.169086185 |
| Rust | 0.0574 | 0.0567 | 0.0586 | -0.169086185 |
| Python | 10.0939 | 9.8837 | 11.2231 | -0.169086185 |

### matmul

Dense matrix multiply, naive triple loop, 300x300 doubles.

| Language | Median (s) | Min (s) | Max (s) | Result |
|---|---|---|---|---|
| Flow | 0.0403 | 0.0392 | 0.0414 | 202497.750000 |
| C | 0.0426 | 0.0405 | 0.0437 | 202497.750000 |
| Rust | 0.0409 | 0.0403 | 0.0421 | 202497.750000 |
| Python | 7.7846 | 7.5972 | 8.0983 | 202497.750000 |

### spectral

Spectral norm, N=500, 10 power iterations (Benchmarks Game).

| Language | Median (s) | Min (s) | Max (s) | Result |
|---|---|---|---|---|
| Flow | 0.0159 | 0.0158 | 0.0160 | 1.274224116 |
| C | 0.0158 | 0.0157 | 0.0159 | 1.274224116 |
| Rust | 0.0162 | 0.0159 | 0.0165 | 1.274224116 |
| Python | 3.9735 | 3.8574 | 4.0955 | 1.274224116 |

### mandelbrot

Mandelbrot membership count, 400x400 grid, 100 iterations.

| Language | Median (s) | Min (s) | Max (s) | Result |
|---|---|---|---|---|
| Flow | 0.0190 | 0.0187 | 0.0193 | 39687 |
| C | 0.0191 | 0.0187 | 0.0198 | 39687 |
| Rust | 0.0313 | 0.0302 | 0.0317 | 39687 |
| Python | 0.9356 | 0.9179 | 1.0424 | 39687 |

## Compile time

Measured once per benchmark. Compile time is excluded from every
workload number.

| Benchmark | Flow transpile (s) | clang on generated C (s) | clang on hand C (s) | rustc (s) |
|---|---|---|---|---|
| fib | 0.04 | 0.14 | 0.12 | 0.17 |
| nbody | 0.05 | 0.21 | 0.16 | 0.23 |
| matmul | 0.04 | 0.19 | 0.14 | 0.25 |
| spectral | 0.04 | 0.26 | 0.17 | 0.24 |
| mandelbrot | 0.04 | 0.15 | 0.11 | 0.18 |

## Method

- Each program times only its workload with a monotonic clock and
  prints the elapsed seconds itself. Compiler time, transpile time,
  and process startup are excluded.
- One warmup run, then 5 timed repetitions per program.
  Median, min, and max of the timed repetitions are reported.
- Identical algorithms, data sizes, and double precision floats in
  every language. Sources live in benchmarks/publish/, and the Python
  ones in benchmarks/baselines/python/publish/.
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

- Source SHA: b57895b270760126a191777f6138bb938d8b940f
- Flow: Flow 2.0.0
- CPU: Intel(R) Xeon(R) Processor @ 2.30GHz, 4 cores, 7 GB RAM
- C compiler: Ubuntu clang version 18.1.3 (1ubuntu1)
- Python: Python 3.12.13
- Rust: rustc 1.94.0 (4a4ef493e 2026-03-02)
- Flags: clang -O3 -march=native

## Reproduce

```bash
./flow tool bench_publish
```

This regenerates benchmarks/RESULTS.md in place. A full run takes
a few minutes; most of that is the Python repetitions.
