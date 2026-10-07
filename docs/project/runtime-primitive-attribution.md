# Runtime primitive attribution

Issue [#745](https://github.com/flooooooooooow/flow/issues/745) asks for an
audit of core runtime and stdlib primitives against idiomatic Python and
against a matching native C baseline, then for focused work on any avoidable
Flow tax.

The measurement authority is `./flow tool bench_harness` (the #728
cross-dimensional harness). Performance numbers themselves are local-only:
do not treat stored timings from another machine as a regression.

## Required primitives

| Primitive | Workload | Algorithm |
|---|---|---|
| Function calls | `runtime/calls` | 1e6 direct calls |
| Loops / branches | `runtime/loops` | 1e6 increment |
| Arrays / spans | `runtime/arrays` | 10000 fills of 1000 `i32`s |
| Strings | `runtime/strings` | ASCII upper-case copy |
| String concat | `runtime/string_concat` | eight-part join, 50k rows |
| Parse / format | `runtime/parse_format` | integer scan + format |
| Buffered I/O | `runtime/buffered_io` | one read, in-place scan, one write |
| Structs | `runtime/structs` | one `Point` record |
| Allocation / free | `runtime/allocation` | 50000 × 64-byte malloc/free |
| Hash / map | `runtime/hashmap` | open-addressed insert + lookup |
| Sorting / search | `runtime/sorting` | heapsort + binary search |
| Reductions | `runtime/numerical` | sum / min / max / sum-of-squares |
| FFI scalar call | `runtime/ffi_scalar` | 20000 noinline scalar calls (#737) |
| FFI batched pointer | `runtime/ffi_batch` | 64 calls over 4096 `i64`s (#737) |
| FFI buffer handoff | `runtime/ffi_buffer` | zero-copy borrow, same sum (#737) |

Each runtime workload has three subjects when the files exist:

- Flow under `benchmarks/cross_harness/runtime/<name>/`
- CPython under `benchmarks/baselines/python/cross_harness/runtime/<name>/`
- Native C under `benchmarks/baselines/native/cross_harness/runtime/<name>/`

The native program does the same user-visible work and is compiled with
`clang -O3 -march=native -lm`, the same flags as generated Flow C. That
separates language/runtime overhead from the algorithm.

`./flow tool bench_harness --check-runtime-natives` fails if any runtime
`.flow` workload is missing its `.c` twin.

## Ratios

Each result row records:

| Field | Meaning |
|---|---|
| `flow_vs_python` | Flow median / CPython median |
| `flow_vs_native` | Flow median / native median |
| `python_vs_native` | CPython median / native median |

`flow_vs_native` is the Flow tax. A promoted hot primitive should stay at
or under 1.05 on a quiet local run. Suite scores are not averaged: a loss
stays on its own row.

```bash
./flow tool bench_harness --smoke --out /tmp/flow-runtime-attr.json
./flow tool bench_harness --eval-tax /tmp/flow-runtime-attr.json
```

`--eval-tax` prints `ok`, `tax` (>1.05) or `no_native` per row. It is a
classifier. CI does not gate on it.

## Complexity

These are the expected bounds for the stdlib and harness copies:

| Primitive | Expected |
|---|---|
| `hash_i64` / `hash_string` | O(1) mix of both words / O(length) djb2, not a constant |
| `hashmap_i64_i64_insert` | amortized O(1); the table doubles before load 1/2 |
| `hashmap_i64_i64_get` | expected O(1) linear probe |
| Heapsort | O(n log n) time, O(1) extra |
| Binary search | O(log n) |
| Reductions | O(n) |

`hashmap_string_i32` still has no insert/get (#1448). That gap is
listed here so a suite mean cannot hide it.

## Promoted hot primitives

The 5% tax bar applies to rows that do enough work to be timed:

- `runtime_loops`, `runtime_calls`, `runtime_strings`
- `runtime_string_concat`, `runtime_parse_format`, `runtime_buffered_io`
- `runtime_allocation`, `runtime_hashmap`, `runtime_sorting`, `runtime_numerical`

`runtime_structs` stays in the suite for coverage but is too small for a
stable tax reading.

The #740 memory profiler is enabled only on the memory suite so a runtime
`flow_vs_native` ratio is not the wrapper tax.

## Audit results (2026-10-08)

Measured on macOS arm64 (Apple silicon, 14 threads) at `20ceebe0`. The
harness medians for these rows are 5 to 20 ms per run, so a busy machine
moves them by more than the 5% bar. For the verdicts each Flow binary and
its native twin ran 200 times, interleaved, exec to exit, and the table
gives the minimum and the median ratio. CPython is the harness median from
the same day. Times are microseconds.

| Row | Flow min | Native min | flow/native (min) | flow/native (median) | CPython median | Verdict |
|---|---:|---:|---:|---:|---:|---|
| `runtime_calls` | 1289 | 1286 | 1.002 | 1.010 | 83700 | ok |
| `runtime_loops` | 1047 | 1064 | 0.984 | 1.002 | 74200 | ok |
| `runtime_arrays` | 1534 | 1525 | 1.006 | 1.026 | 859400 | ok |
| `runtime_strings` | 1608 | 1578 | 1.019 | 1.031 | 1119000 | ok |
| `runtime_string_concat` | 4229 | 1862 | 2.271 | 2.119 | 561200 | tax, #1447 |
| `runtime_parse_format` | 3263 | 15616 | 0.209 | 0.220 | 148000 | ok |
| `runtime_buffered_io` | 2129 | 2349 | 0.906 | 0.943 | 28300 | ok |
| `runtime_structs` | 917 | 905 | 1.013 | 1.023 | 33500 | coverage only |
| `runtime_allocation` | 1947 | 1925 | 1.011 | 1.016 | 38300 | ok after the ring fix |
| `runtime_hashmap` | 1292 | 1291 | 1.001 | 1.016 | none | ok |
| `runtime_sorting` | 1238 | 1170 | 1.058 | 1.009 | 126800 | ok (median) |
| `runtime_numerical` | 1071 | 1061 | 1.009 | 1.015 | 27600 | ok |
| `runtime_ffi_scalar` | 949 | 933 | 1.017 | 1.007 | none | ok |
| `runtime_ffi_batch` | 951 | 944 | 1.007 | 1.022 | none | ok |
| `runtime_ffi_buffer` | 961 | 939 | 1.023 | 1.024 | none | ok |

Flow is faster than CPython on every row with a CPython twin, by 13x
(`runtime_buffered_io`) to 700x (`runtime_strings`).

What the audit changed:

- `runtime_allocation` read 1.56x. The native twin freed each block before
  anything could see it, so clang removed every `malloc`/`free` pair and the
  native program did no heap work. Flow's #740 counting wrappers kept the
  calls. Both programs now keep each block live in a 16-slot ring, and the
  ratio is 1.011. The wrappers themselves cost about 1%.
- `hash_i64` hashed only the low 32 bits of the key, so keys that differ
  only above bit 31 (`i << 32`, packed pairs) all landed in one probe
  cluster and each map operation was O(n). It now folds the high word in
  first. `tests/lang/test_hashmap_i64.flow` checks 64 such keys spread over
  a 64-slot table. The harness copy and its native twin use the same hash.

## Remaining gaps

- `runtime_string_concat` is 2.1x native: a short `+` chain is one heap
  allocation and a separate scan, where C copies into a stack buffer (#1447).
- `hashmap_string_i32` has create/len only; insert/get need a key ownership
  decision (#1448).
- No CPython twin for `runtime_hashmap` or the FFI rows (new `.py` files are
  refused).
- `runtime_structs` is a coverage row. It has no tax verdict.
- Any new measured `tax` on a promoted row becomes its own child issue
  rather than being folded into a headline geometric mean.
