# Flow benchmark results

Date: 2026-09-08

Flow compiles to C. The comparison that matters is Flow against
hand-written C built by the same clang with the same flags. Rust and
plain CPython run the same algorithms at the same sizes for context.

## Summary

| Benchmark | Flow median (s) | C median (s) | Rust median (s) | Python median (s) | Flow / C |
|---|---|---|---|---|---|
| fib | 0.0360 | 0.0376 | 0.0375 | 2.1634 | 0.96x |
| nbody | 0.1000 | 0.0752 | 0.0808 | 9.8060 | 1.33x |
| matmul | 0.0640 | 0.0691 | 0.0396 | 7.0867 | 0.93x |
| spectral | 0.0160 | 0.0154 | 0.0158 | 3.8831 | 1.04x |
| mandelbrot | 0.0200 | 0.0186 | 0.0231 | 0.8829 | 1.08x |

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
| Flow | 0.0360 | 0.0360 | 0.0400 | 9227465 |
| C | 0.0376 | 0.0373 | 0.0380 | 9227465 |
| Rust | 0.0375 | 0.0371 | 0.0378 | 9227465 |
| Python | 2.1634 | 2.1624 | 2.1831 | 9227465 |

### nbody

Outer solar system, 5 bodies, 1,000,000 steps (Benchmarks Game).

| Language | Median (s) | Min (s) | Max (s) | Result |
|---|---|---|---|---|
| Flow | 0.1000 | 0.0960 | 0.1000 | -0.169086185 |
| C | 0.0752 | 0.0745 | 0.0874 | -0.169086185 |
| Rust | 0.0808 | 0.0792 | 0.0847 | -0.169086185 |
| Python | 9.8060 | 9.6097 | 10.4351 | -0.169086185 |

### matmul

Dense matrix multiply, naive triple loop, 300x300 doubles.

| Language | Median (s) | Min (s) | Max (s) | Result |
|---|---|---|---|---|
| Flow | 0.0640 | 0.0480 | 0.0640 | 202497.750000 |
| C | 0.0691 | 0.0680 | 0.0713 | 202497.750000 |
| Rust | 0.0396 | 0.0395 | 0.0403 | 202497.750000 |
| Python | 7.0867 | 6.9687 | 7.3106 | 202497.750000 |

### spectral

Spectral norm, N=500, 10 power iterations (Benchmarks Game).

| Language | Median (s) | Min (s) | Max (s) | Result |
|---|---|---|---|---|
| Flow | 0.0160 | 0.0160 | 0.0200 | 1.274224116 |
| C | 0.0154 | 0.0154 | 0.0155 | 1.274224116 |
| Rust | 0.0158 | 0.0158 | 0.0158 | 1.274224116 |
| Python | 3.8831 | 3.8793 | 4.1127 | 1.274224116 |

### mandelbrot

Mandelbrot membership count, 400x400 grid, 100 iterations.

| Language | Median (s) | Min (s) | Max (s) | Result |
|---|---|---|---|---|
| Flow | 0.0200 | 0.0160 | 0.0200 | 39687 |
| C | 0.0186 | 0.0185 | 0.0188 | 39687 |
| Rust | 0.0231 | 0.0230 | 0.0232 | 39687 |
| Python | 0.8829 | 0.8798 | 0.8946 | 39687 |

## Compile time

Measured once per benchmark. Compile time is excluded from every
workload number.

| Benchmark | Flow transpile (s) | clang on generated C (s) | clang on hand C (s) | rustc (s) |
|---|---|---|---|---|
| fib | 0.27 | 0.14 | 0.12 | 0.18 |
| nbody | 0.29 | 0.19 | 0.17 | 0.24 |
| matmul | 0.27 | 0.17 | 0.13 | 0.23 |
| spectral | 0.33 | 0.19 | 0.22 | 0.25 |
| mandelbrot | 0.27 | 0.15 | 0.12 | 0.19 |

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

- CPU: Intel(R) Xeon(R) Processor @ 2.30GHz, 4 cores, 7 GB RAM
- C compiler: Ubuntu clang version 18.1.3 (1ubuntu1)
- Python: Python 3.12.13
- Rust: rustc 1.94.0 (4a4ef493e 2026-03-02)

## Reproduce

```bash
./benchmarks/run_publish.sh
```

This regenerates benchmarks/RESULTS.md in place. A full run takes
a few minutes; most of that is the Python repetitions.

### MLIR Opt: Automatic memory layout transformations (AoSoA)
- **AoS execution time**: 12.2181s
- **SoA execution time**: 12.0111s
- **Improvement**: 1.02x speedup
