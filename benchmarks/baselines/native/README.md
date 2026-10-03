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
