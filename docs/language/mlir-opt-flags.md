# MLIR optimization flags

When compiling with the MLIR backend (`--mlir`), pass `--optimize` to run
`mlir-opt` through Flow’s pass pipeline.

## Levels

| Flag | Effect |
|------|--------|
| `--opt-level O0` | No passes |
| `--opt-level O1` | canonicalize, CSE, symbol-dce |
| `--opt-level O2` (default) | O1 + inline, sccp, mem2reg, LICM, affine-loop-fusion |
| `--opt-level O3` | O2 + affine-super-vectorize |

## Toggles

Disable individual passes (level gates still apply):

```
--no-vectorization   # O3 affine-super-vectorize
--no-loop-fusion     # O2+ affine-loop-fusion
--no-mem2reg
--no-sccp
--no-licm
--no-cse             # CSE stand-in for GVN
--no-dce             # symbol-dce + trailing canonicalize
--no-inline
```

Inspect the pipeline without running `mlir-opt`:

```bash
python3 -m flow.transpiler --print-pass-pipeline --opt-level O2 --no-inline
./flow mlir examples/basics/hello_world.flow --optimize --opt-level O3 --no-vectorization
```

`--opt-report` prints pass statistics using the same flag set.

## Generator-side vectorization

Independently of `--optimize`, the generator rewrites simple elementwise
counted loops itself:

```
for i in 0 to n { out[i] = a * x[i] + y[i] }
```

over `f32` or `i32` memref bases becomes a step-4 `scf.for` of
`vector.transfer_read` / `vector.transfer_write` plus a scalar remainder loop,
marked in the IR with `// flow: vectorized elementwise f32 loop (VF=4)`.
Loop-carried accumulators and pointer bases stay scalar.

The lowering pipeline runs `--convert-vector-to-scf` before `--convert-scf-to-cf`
and `--convert-vector-to-llvm` before `--convert-func-to-llvm`; without both,
`vector.transfer_read` reaches `mlir-translate` as an unregistered op.

> `affine-super-vectorize` and `affine-loop-fusion` still need affine loops,
> which the generator does not emit; they remain soft no-ops.
