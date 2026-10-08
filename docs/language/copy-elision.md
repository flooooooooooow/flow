# Copy elision (#732)

flowc elides avoidable full-object copies of aggregates after last-use /
uniqueness is known. There is no source-level move syntax: the C and MLIR
backends decide when a record update, a large return, or a last-use local
can be constructed in place.

The first slice (merged PR #1338) built `Name { ..base, f: v }` into a
let, a distinct assignment, or a last-use return. This page records the
remaining lowering: destination-passing, overwrite-dependence, the copy
metric, MLIR parity, and coverage for arrays, closures and matrices.

## Destination-passing (sret)

A Flow-defined function that returns a named user struct writes the
result through a hidden destination pointer `__flowc_sret`:

- **Single-module** compilation (`flow run file.flow`, `tests/cgen`):
  the C signature is `void foo(T* __flowc_sret, args)`. A let or
  assignment `q = foo(...)` becomes `foo(&q, ...)`. An expression-position
  call allocates a temporary, passes its address, and yields the
  temporary.
- **Bundles** (`FLOWC_BUNDLE=1`, including compiler self-host): the public
  signature stays `T foo(args)`. The callee declares
  `T __flowc_sret_slot; T* __flowc_sret = &__flowc_sret_slot;` and
  `return *__flowc_sret`. C NRVO typically maps that slot onto the
  caller's return object. Pointer ABI is withheld for every module in a
  bundle, not only later ones: the first module has an empty signature
  table and would otherwise change helpers that later modules still call
  by value.

Pointer-ABI sret is withheld for `main`, exported / `@flow_api`
functions, library units (`FLOWC_LIBRARY=1`), bundles, functions taken
as values, and externs, so C function pointers and the export ABI stay
stable.

A record-update return constructs into `*__flowc_sret` (copy the base,
write listed fields). The destination is distinct from the base, so
value semantics hold without mutating the source.

## Overwrite-dependence

Last-use / uniqueness proves that storage is available. It does **not**
prove that an in-place write order exists.

For a same-storage update `y_j = f_j(x_{R_j})` there is an
overwrite-dependence edge `j -> i` whenever output `j` reads old slot
`i` and `i != j`. Writing `i` destroys `x_i`, so `j` must be written
first. Zero-temporary construction exists if and only if that graph is
acyclic: a topological order is sufficient. A cycle falls back to the
statement-expression temporary.

Concrete counterexample (left rotation / a field swap):

```
q = Point { ..q, x: q.y, y: q.x }
```

The edges `x -> y` and `y -> x` form a cycle. Naïve forward writes on
`[1, 2]` yield `[2, 2]`. flowc keeps the temporary so the result is
`[2, 1]`.

An acyclic case is written in place:

```
q = Point { ..q, x: q.y, y: 0 }
```

`x` reads `y`, so `x` is written first (while `y` is still old), then
`y`.

Unlisted fields are not written, so a read of an unlisted slot is not a
dependence. A whole-object read of the destination counts as a read of
every listed slot.

## Copy-count metric (#728)

The opt-in memory profiler (`FLOW_MEM_PROFILE`) counts each instrumented
aggregate copy:

- `copies`: copy volume in bytes (unchanged)
- `copy_count`: number of copy operations

Compiler-emitted struct assignments and array-field `memcpy`s call
`flow_mem_note_copy`. Routed libc `memcpy` and string helpers already
did. `./flow tool bench_harness` records `copy_count` on every Flow
subject next to `copies`.

## MLIR

`mlirgen.flow` insertvalues listed fields onto the base SSA. A second
field-by-field `stabilize` / alloca round-trip is skipped for
record-update lets and returns. The emitter writes
`// flowc.copy_elision record-update` on those paths.

## Arrays, closures, matrices

- **Arrays.** An array-field update memcpys straight into the destination
  object. It uses no `__flowc_sl` temporary. A sized-array assignment notes one copy
  (`flow_mem_note_copy(sizeof(dest))`) and memcpys. Last-use of a local
  array still needs that one copy into the caller or the other binding;
  the extra statement-expression object is gone.
- **Closures.** A last-use return of a fat pointer (`{fn, env}`) is a
  two-word move. The captured environment is not memcpy'd.
- **Matrices.** A matrix is a named struct (often with an array field).
  Destination-passing, overwrite-dependence and array-field memcpy apply
  unchanged. `tests/cgen/copy_elision_matrix.flow` is a 2×2 record
  pipeline that must not emit `__flowc_sl` on the let-bound / sret
  paths.

## Tests

- `tests/cgen/copy_elision.flow`: structural C for lets, assignments,
  sret returns, and the expression-position temporary
- `tests/cgen/copy_elision_dep.flow`: acyclic in-place vs cyclic temp
- `tests/cgen/copy_elision_matrix.flow`: matrix / array / closure
- `tests/lang/test_copy_elision.flow`: value semantics, including a
  dest==base swap
- `compiler/fixtures/mlir/record_update.flow`: MLIR golden

Related: [Export ABI](export-abi.md), [Memory](../library/memory.md),
parent issue #727.
