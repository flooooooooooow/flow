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
| `hash_i64` / `hash_string` | O(1) mix / O(length) djb2, not a constant |
| `hashmap_i64_i64_insert` | amortized O(1); the table doubles before load 1/2 |
| `hashmap_i64_i64_get` | expected O(1) linear probe |
| Heapsort | O(n log n) time, O(1) extra |
| Binary search | O(log n) |
| Reductions | O(n) |

`hashmap_string_i32` still has no insert/get. That gap is
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

## Remaining gaps

- `hashmap_string_i32` create/len only; no insert/get.
- No CPython twin for `runtime_hashmap` (new `.py` files are refused).
- `runtime_structs` is a coverage row. It has no tax verdict.
- `runtime_string_concat` still heaps every `+` chain; matching C can keep
  the 36-byte result on the stack. That headroom needs a compiler
  short-string / stack-concat slice.
- Any other measured `tax` on a promoted row should become its own child
  issue rather than being folded into a headline geometric mean.
