# SIMD-aware C lowering for hot loops

The production C backend does not wait on the MLIR optimizer to emit
competitive CPU loops. Counted numeric loops lower to compiler-recognizable
C, and a small set of f32/f64 kernels additionally lower to portable 128-bit
vector extensions. Every fast path has a scalar fallback. Integer results
and stores are exact. Vector sum and dot reassociate floating-point addition,
as the clang `vectorize(enable)` hint on the scalar loop already allows.

Parent issue: [#739](https://github.com/flooooooooooow/flow/issues/739)
(performance epic [#727](https://github.com/flooooooooooow/flow/issues/727)).

## What the C backend emits

| Flow form | Generated C |
|---|---|
| `for i in 0 to n { y[i] = ... }` with a straight-line body | `#pragma omp simd` (with `reduction` when the body is `acc = acc ⊕ expr`) when `_OPENMP` is defined; otherwise clang `loop vectorize` or GCC `ivdep` |
| Unit-stride `dst[i] = src[i]` on pointers, arrays, or spans | One `memcpy` of `(hi - lo) * sizeof(element)` when region inference proves the two regions disjoint; spans go through `.data`, and with runtime checks each span gets one range test. Otherwise the ordered loop stays (#1417) |
| Counted `while i < n { ...; i = i + 1 }` | A C `for (; i < n; i = i + k)` with the clang and GCC loop hints. OpenMP simd is left out: it needs an init clause and would privatize `i`. `continue` and `@max_iterations` keep the `while`. Overlapping while-copies stay elementwise so they keep loop order |
| Clip / min / max `if` / `else` stores to the same `base[i]` | A C ternary (`?:`), which the auto-vectorizer treats as a select. An `if` without `else` keeps the branch, since the select would read `base[i]` when the guard is false. Arbitrary predicate reductions stay scalar |
| Recognized f32/f64 kernels (fill, scale, axpy, add, sum, dot) | GCC/clang `vector_size(16)` strip-mined loops behind `FLOWC_HAS_V128`, plus a scalar tail. See the conditions below |

`FLOWC_HAS_V128` is 1 when `__SSE2__`, `__AVX__`/`__AVX2__`, `__ARM_NEON`, or
`__aarch64__` is defined (Tier-1 x86-64 and arm64). Otherwise the pragma-hinted
scalar loop is the only path.

Loop-carried scalars that are not reductions (`acc = acc * 10 + i`) get only
the clang hint: OpenMP simd and GCC ivdep would promise independence they do
not have.

## Kernel conditions

A kernel loads four f32 (or two f64) lanes before it stores any of them. The
scalar loop stores one element before it loads the next, so the two agree
only when no store can feed a later load. The C backend uses a kernel when:

- every array the loop reads is the destination itself at the same index, or
  region inference proves it disjoint from the destination. Two pointer or
  span parameters may be shifted views of one buffer (`dst = src + 1`), and
  then the scalar loop is a recurrence;
- the scalar factor `k` reads no memory and calls nothing, because the
  kernel evaluates it once before the loop;
- all arrays share the element type;
- runtime checks are off. The kernel moves whole lanes with `memcpy`, which
  would bypass the per-index bounds tests.

Fill reads no memory and sum and dot store nothing, so they need only the
last three conditions.

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
x86-64, `.4s`/`fadd`/`fmla` on arm64). When `aarch64-linux-gnu-gcc` or
`x86_64-linux-gnu-gcc` is on PATH, the other ISA is compiled the same way so
one host can still produce both listings. Other hosts skip.

The MLIR backend is not required to avoid a scalar deficit on these forms.
