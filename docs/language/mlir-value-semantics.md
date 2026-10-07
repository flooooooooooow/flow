# MLIR tensor value semantics

Flow emits array and tensor computations as immutable SSA values in the
MLIR `tensor` dialect. One-Shot Bufferization then chooses storage after
global alias analysis. It may reuse storage in place when legal; **a memref
result is not automatically a proof of disjointness**. Later optimizations
may assume non-aliasing only where the bufferization result, region/noalias
analysis, or an explicit structural argument actually proves it.

This is the contract behind [#664](https://github.com/flooooooooooow/flow/issues/664).
Pass flags that run the pipeline live in [MLIR optimization flags](mlir-opt-flags.md).

## Value form

Elementwise tensor intrinsics (`tensor_add`, `tensor_sub`, `tensor_mul`,
`tensor_div`, `tensor_scale`, `tensor_add_scalar`) write a fresh
`tensor.empty` destination and a `linalg.generic`. The first operand is
never used as `outs` when the result is a tensor, so the operation has
value semantics and One-Shot Bufferization can reuse storage only after
it proves the operand is dead.

Mutable tensor locals stay SSA. They are not stored through `llvm.alloca`.
A counted loop that rebinds a tensor therefore carries the value as an
`scf.for` `iter_args` result and yields the next tensor. That is the
destination-passing form One-Shot Bufferization needs to avoid a heap
allocation on every iteration.

```flow ignore="tensor_f32 is MLIR-only; tests/mlir_commands (mlir_tensor_hot_loop) compiles the fixture" from="compiler/fixtures/mlir_opt/tensor_hot_loop.flow"
function accumulate(a: tensor_f32, b: tensor_f32, n: i32) -> tensor_f32 {
    let mut acc: tensor_f32 = a
    for i in 0 to n step 1 {
        acc = tensor_add(acc, b)
    }
    return acc
}
```

`tensor_add` is an extern declared in that fixture,
`compiler/fixtures/mlir_opt/tensor_hot_loop.flow`.

## Function boundaries

Tensor-returning functions keep tensor arguments and results in the
emitted IR. `one-shot-bufferize{bufferize-function-boundaries=1}` (O1 and
above) rewrites those boundaries to memrefs. After that pass the module
has no `tensor<` types.

## Alias-aware follow-on opts

When a particular destination/source pair is proven non-aliasing, LICM can
hoist invariant `memref.dim` / `memref.load` queries and affine
vectorization can use the stronger dependence result. Merely having passed
through One-Shot Bufferization does not grant that proof: in-place
bufferization deliberately creates aliases when it is semantically legal.

The regressions in `tests/scripts/mlir_bufferize_boundary.flow` cover the
destination form, function-boundary bufferization, hot-loop SSA,
allocation-free loops, explicit alias-free load-hoist/vectorization
examples, and non-commutative memref operand ordering. The optimizer-level
checks skip when `mlir-opt` is not installed.
