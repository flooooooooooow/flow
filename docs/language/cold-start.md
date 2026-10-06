# Compiled-program cold start

Tiny Flow programs should start faster than the equivalent CPython invocation
on Tier-1 platforms. That only holds if the generated executable does not pay
for runtime pieces it never uses.

## What `flow compile` links

`./flow compile` (and `./flow run` on the C backend) emit C with flowc and
link against the Flow runtime archive. The archive still contains optional
pieces :  Python embedding, the Metal GPU shim, OpenSSL, OpenMP :  so a program
that calls them keeps working.

Those optional libraries must not become load commands on a program that
never reaches them. Loading Python3, Metal/Foundation and OpenSSL at exec
time was several milliseconds of dyld work on macOS for a `return 0`
program. The driver therefore runs a **probe link** that omits those
framework groups and dead-strips:

- If the probe succeeds, the lean binary is kept.
- If a needed symbol is missing, the driver falls back to the historical
  full link, so a program that uses GPU, Python or crypto is unchanged.

`FLOW_NO_LINK_TRIM=1` forces the full link. Sanitizer builds always take it,
so interceptors stay resolvable.

Generated C for a program that does not need Flow runtime initialization
contains no constructor or destructor attributes. Minimal programs therefore
do no Flow-specific work before `main`.

## Measuring startup

`./flow tool compile_bench` times flowc emit, the C toolchain and the
program run. Each JSON row is machine-readable (`run_ms`, `bin_bytes`,
cold/warm totals, and when the compiler supports it, per-phase
`FLOWC_PROFILE` fields).

To compare against an equivalent Python invocation, pass the matching
source to `--python-code`. Each row then also reports `python_ms` and
`run_vs_python_x100` (Flow `run_ms` as a percentage of the Python minimum;
values under 100 mean Flow was faster):

```
./flow tool compile_bench --repeat 5 --python-code 'print("Hello, world!")' \
    examples/basics/hello_world.flow
```

`--python-code` without a following argument exits 2.

The #728 cross-harness (`./flow tool bench_harness`) has a `cold/` suite
(hello world, tiny arithmetic, file transform, JSON-like parse/format, CLI
one-shot) with CPython twins under `benchmarks/baselines/python/cross_harness`.

## Related

- [Running Flow](flow-run.md)
- Issue #746 (cold start) under parent #727
- `tests/scripts/cold_start.flow` and `tests/scripts/size_regression.flow`
