# Compiler-recognized standard-library contracts

Most Flow standard-library code is ordinary Flow. A small number of library surfaces carry compiler-recognized contracts so the backends can preserve source semantics while selecting native operations.

## `@libm`

`@libm` marks the canonical standard-library wrappers that are allowed to lower to the platform math implementation or an equivalent backend intrinsic. The compiler must resolve the call to an `@libm` declaration before using the special lowering; a user-defined function that merely shares a name such as `sin`, `exp`, or `sqrt` is still an ordinary Flow function and must be called normally.

This attribute is intended for the shipped math shims, not as a general promise that arbitrary user code can be replaced by libm. C lowering may retain the platform libm symbol, while MLIR may select the corresponding `math.*` operation when the resolved declaration carries this contract.

## `complex_linalg`

`complex_linalg` is the pure-Flow complex linear-algebra module at `lib/stdlib/complex_linalg.flow`. It exposes the `CMat` matrix representation plus allocation/clone/access helpers, complex matrix multiplication (`cgemm` and `cgemm_alpha_beta`), LU factorization/solve (`cgetrf`, `cgetrs`, `csolve`), and a small matrix-exponential implementation (`cmat_exp`).

The module currently owns its matrix storage explicitly through `cmat_new`/`cmat_free`; callers are responsible for matching allocations with frees. It is a correctness/reference implementation rather than a claim that every operation is already mapped to an optimized BLAS/LAPACK backend.
