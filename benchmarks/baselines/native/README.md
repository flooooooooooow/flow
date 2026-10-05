# Native benchmark subjects

The C programs here are native references for Flow programs in
`benchmarks/cross_harness/`. Each one does the same work as its Flow twin so
`./flow tool bench_harness` can separate Flow's generated-code overhead from
the algorithm itself.

| Directory | Twin of | Run by |
|---|---|---|
| `cross_harness/<suite>/<name>/` | `benchmarks/cross_harness/<suite>/<name>/*.flow` | `./flow tool bench_harness` |

The harness compiles each subject with `clang -O3 -march=native -lm`, the same
flags used for generated Flow C.

Runtime twins (required by `./flow tool bench_harness --check-runtime-natives`):

| Directory | Work |
|---|---|
| `cross_harness/runtime/calls` | 1e6 direct calls |
| `cross_harness/runtime/loops` | 1e6 increment |
| `cross_harness/runtime/arrays` | fill 1000 `i32`s |
| `cross_harness/runtime/structs` | one `Point` |
| `cross_harness/runtime/strings` | ASCII upper-case copy |
| `cross_harness/runtime/string_concat` | eight-part join |
| `cross_harness/runtime/parse_format` | integer scan + format |
| `cross_harness/runtime/buffered_io` | one read, in-place scan, one write |
| `cross_harness/runtime/allocation` | 1000 × 64-byte malloc/free |
| `cross_harness/runtime/hashmap` | open-addressed insert + lookup |
| `cross_harness/runtime/sorting` | heapsort + binary search |
| `cross_harness/runtime/numerical` | sum / min / max / sum-of-squares |

See [runtime primitive attribution](../../../docs/project/runtime-primitive-attribution.md).
