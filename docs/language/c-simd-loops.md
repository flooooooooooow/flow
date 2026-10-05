# SIMD-aware C lowering for hot loops

The production C backend does not wait on the MLIR optimizer to emit
competitive CPU loops. Counted numeric loops lower to compiler-recognizable
C, and a small set of f32/f64 kernels additionally lower to portable 128-bit
vector extensions. Scalar results stay exact: every fast path has a scalar
fallback.

Parent issue: [#739](https://github.com/flooooooooooow/flow/issues/739)
(performance epic [#727](https://github.com/flooooooooooow/flow/issues/727)).

## What the C backend emits

| Flow form | Generated C |
|---|---|
| `for i in 0 to n { y[i] = ... }` with a straight-line body | `#pragma omp simd` (with `reduction` when the body is `acc = acc ⊕ expr`) when `_OPENMP` is defined; otherwise clang `loop vectorize` or GCC `ivdep` |
| Unit-stride `dst[i] = src[i]` on pointers, arrays, or spans | `memmove` of `(hi - lo) * sizeof(element)`; spans go through `.data`. Runtime checks, when enabled, become one range test rather than a per-index loop |
| Counted `while i < n { ...; i = i + 1 }` | The same C `for` as the equivalent counted loop, including SIMD hints. `continue` and `@max_iterations` keep the `while`. Overlapping while-copies stay elementwise so they keep loop order |
| Clip / min / max `if` / `else` stores to the same `base[i]` | A C ternary (`?:`), which the auto-vectorizer treats as a select. An `if` without `else` keeps the branch, since the select would read `base[i]` when the guard is false. Arbitrary predicate reductions stay scalar |
| Recognized f32/f64 kernels (fill, scale, axpy, add, sum, dot) | GCC/clang `vector_size(16)` strip-mined loops behind `FLOWC_HAS_V128`, plus a scalar tail |

`FLOWC_HAS_V128` is 1 when `__SSE2__`, `__AVX__`/`__AVX2__`, `__ARM_NEON`, or
`__aarch64__` is defined (Tier-1 x86-64 and arm64). Otherwise the pragma-hinted
scalar loop is the only path.

Loop-carried scalars that are not reductions (`acc = acc * 10 + i`) get only
the clang hint: OpenMP simd and GCC ivdep would promise independence they do
not have.

## What is not rewritten

- A branch that is not a same-index select or clip (the skip tests in
  `tests/cgen/for_vectorize_pragma_skip.flow`)
- Calls outside the math set (`sin`/`cos`/`exp`/`log`/`sqrt`/…)
- Nested loops, `break`/`return` in a while that is otherwise counted
- `continue` in a counted while (it would skip the increment in Flow, but
  not in a C `for`)

## Evidence

Generated-C goldens live under `tests/cgen/for_simd_*.flow`. Tier-1 assembly
is `./flow tool tests/scripts/simd_asm.flow`: it compiles the hot-loop kernels
with `cc -O3 -march=native -S` and requires 128-bit SIMD ops (`xmm`/`addps` on
x86-64, `.4s`/`fadd`/`fmla` on arm64). Other hosts skip.

The MLIR backend is not required to avoid a scalar deficit on these forms.
