# Proven restrict / noalias

> **Status:** C and MLIR backends emit `restrict` / `{llvm.noalias}` only
> when a fail-closed provenance certificate proves disjointness (#731).
> A first slice landed in PR #1344. This page describes the certificate
> and the remaining interprocedural / span / struct-field rules.

Flow's ownership and region facts are a performance win only if generated
C and MLIR keep them. A wrong `restrict` is undefined behaviour, so the
backend stays fail-closed: unknown provenance never certifies
disjointness.

## Certificate

A view is `(kind, root, offset, length, known, field)`:

- A local array, struct, or scalar is fresh frame storage.
- Two local views of distinct roots are disjoint.
- Same-root views of different embedded fields are disjoint.
- Same-root, same-field views are disjoint only when both half-open
  intervals `[off, off+len)` are known and do not overlap.
- Two parameters may alias (the caller can pass the same buffer twice).
- A local is disjoint from every parameter.
- Unknown provenance, dynamic slice bounds, and laundering calls fail
  closed.

`span<T>` is tracked as a view so overlapping slices stay aliasable. The
counter-example is one array `x = [1,2,3,4]`, `src = x[0..3]`,
`dst = x[1..4]`, forward `dst[i] = src[i]`: sequential semantics produce
`[1,1,1,1]`; a false noalias assumption may snapshot the source and
produce `[1,1,2,3]`.

## Function parameters

`restrict` / `{llvm.noalias}` on a shared function is a contract for
every execution. flowc therefore annotates an internal (non-exported,
non-`main`, non-`@flow_api`) function only when:

- it is not address-taken and has a single definition
- this translation unit contains at least one call
- every reachable call's pointer/span arguments are pairwise disjoint

A proof at one call site never annotates an exported ABI.

## Mixed-site clones

When some calls are proven and others are not, the original stays
aliasable. flowc emits an internal clone `__flowc_na_<name>` whose
pointer parameters are restrict-qualified, and rewrites only the proven
direct calls. That is option 3 on #731.

```flow
function mix_add(dst: ptr<i32>, src: ptr<i32>, n: i32) -> i32 { }

function main() -> i32 {
    let mut a: array<i32, 4> = [1, 2, 3, 4]
    let mut b: array<i32, 4> = [5, 6, 7, 8]
    mix_add(a, b, 4)   # rewritten to __flowc_na_mix_add
    mix_add(a, a, 4)   # stays on the aliasable mix_add
    return 0
}
```

## Span `.data` temps

A span parameter is a struct in C and is never itself `restrict`. When
every reachable call (or the specialized clone) proves the span
arguments disjoint, the backend extracts:

```c
T* restrict __flowc_na_d_name = name.data;
```

and indexes through that temporary so the C/LLVM vectorizer sees
noalias on the payload pointer.

## Struct-field provenance

`.data` on a span still inherits the span's view. Other fields:

- a pointer/span field of a struct literal inherits the initializer
- an embedded array or struct field of a local is a distinct LOCAL root
  keyed by field name
- assignment to the binding or any of its fields erases provenance

```flow
struct Pair {
    xs: array<i32, 4>,
    ys: array<i32, 4>
}

function demo_pair_fields() -> void {
    let mut pair: Pair = Pair { xs: [1, 2, 3, 4], ys: [5, 6, 7, 8] }
    let px: ptr<i32> = pair.xs
    let py: ptr<i32> = pair.ys
    # px and py are disjoint; an internal add(px, py, 4) may be restrict
}
```

## What still fails closed

- dynamic slice bounds
- calls that launder a pointer or span
- a buffer passed twice
- exported / `@flow_api` functions
- a pointer copied from a parameter

## Tests

- C goldens: `tests/cgen/noalias_restrict.flow`, `tests/cgen/noalias_vectorize.flow`
- MLIR: `tests/scripts/noalias_mlir.flow`
- Vectorization remarks: `tests/scripts/noalias_vectorize.flow`
- Semantics: `tests/lang/test_noalias_overlap_copy.flow`,
  `tests/lang/test_noalias_mix_clone.flow`,
  `tests/lang/test_noalias_struct_fields.flow`

Related: [spans.md](spans.md) · [LANGUAGE_SPEC](../LANGUAGE_SPEC.md)
