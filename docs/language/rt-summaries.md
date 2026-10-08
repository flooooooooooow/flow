# Cross-module RT / lifetime summaries

> **Status:** Public functions emit a compact effect/lifetime summary.
> Importers consult it during type checking. Summaries are compile-time
> only and are erased before codegen. See
> [issue #765](https://github.com/flooooooooooow/flow/issues/765).

`@rt_safe` and `@lifetime` have to compose across modules. A callback in
one package cannot stay sound if an imported helper allocates, blocks, or
opens a device without the caller seeing that contract.

The summary is a may-effect bitset plus a declared lifetime domain plus
one provenance edge:

| Bit | Meaning |
|---|---|
| ALLOC | may allocate heap / GPU / audio buffers |
| FREE | may free that storage |
| BLOCK | may block or take a lock |
| IO | may do device / file / network I/O |
| UNKNOWN | unprovable imported or extern callable |

Domains follow the current lifetime lattice `callback < frame < request < session < application < persistent`. An unannotated function has no domain.

Local summaries are the least fixed point

```text
E_f = L_f ∪ ⋃ E_callee
```

Imported `$fname` entries are leaves. The lattice is finite, so a worklist
terminates after at most five successful bit insertions per function.

## Rejecting `unknown`

An `extern` that is not a known may-effect and not on the known-safe
allow-list carries `UNKNOWN` rather than an empty contract. `@rt_safe` and
`@lifetime(callback)` reject that bit:

```text
RT-safety violation: 'process' is marked '@rt_safe' but calls 'driver_read',
which has an unknown effect summary (unprovable extern; see
docs/library/rt-safety.md)
```

The allow-list is the math / atomic / bounded-copy / numeric-conversion /
print family that existing realtime paths already call (`sinf`,
`i32_to_f32`, `memcpy`, `printf`, …). `frame` still forbids only heap
create/destroy; `UNKNOWN` is not a frame error.

## Call-graph holes

Named calls, including a uniquely resolved `impl` method, join the
summary worklist. Function-pointer contracts (`with rt_safe`) landed in
#1310. Closure / higher-order callable contracts are the #766 slice
(open PR #1348) and are not reimplemented here. Unresolved dynamic
dispatch, including an ambiguous trait method, stays a conservative
reject from `@rt_safe`.

## Refinement

If a dependency's public contract *refines* the one a client was last
accepted under (`effects_new ⊆ effects_old`, and the declared domain did
not move longer-lived), that client stays accepted. Only effect growth
or a move to a longer-lived (or newly declared) domain can invalidate the
prior result.

`flowc_rt_refines` and `flowc_rt_summaries_refine` implement that relation
over the imported `# Cross-module RT / lifetime summaries

> **Status:** Public functions emit a compact effect/lifetime summary.
> Importers consult it during type checking. Summaries are compile-time
> only and are erased before codegen. See
> [issue #765](https://github.com/flooooooooooow/flow/issues/765).

`@rt_safe` and `@lifetime` have to compose across modules. A callback in
one package cannot stay sound if an imported helper allocates, blocks, or
opens a device without the caller seeing that contract.

The summary is a may-effect bitset plus a declared lifetime domain plus
one provenance edge:

| Bit | Meaning |
|---|---|
| ALLOC | may allocate heap / GPU / audio buffers |
| FREE | may free that storage |
| BLOCK | may block or take a lock |
| IO | may do device / file / network I/O |
| UNKNOWN | unprovable imported or extern callable |

Domains follow the current lifetime lattice `callback < frame < request < session < application < persistent`. An unannotated function has no domain.

Local summaries are the least fixed point

```text
E_f = L_f ∪ ⋃ E_callee
```

Imported `$fname` entries are leaves. The lattice is finite, so a worklist
terminates after at most five successful bit insertions per function.

## Rejecting `unknown`

An `extern` that is not a known may-effect and not on the known-safe
allow-list carries `UNKNOWN` rather than an empty contract. `@rt_safe` and
`@lifetime(callback)` reject that bit:

```text
RT-safety violation: 'process' is marked '@rt_safe' but calls 'driver_read',
which has an unknown effect summary (unprovable extern; see
docs/library/rt-safety.md)
```

The allow-list is the math / atomic / bounded-copy / numeric-conversion /
print family that existing realtime paths already call (`sinf`,
`i32_to_f32`, `memcpy`, `printf`, …). `frame` still forbids only heap
create/destroy; `UNKNOWN` is not a frame error.

## Call-graph holes

Named calls, including a uniquely resolved `impl` method, join the
summary worklist. Function-pointer contracts (`with rt_safe`) landed in
#1310. Closure / higher-order callable contracts are the #766 slice
(open PR #1348) and are not reimplemented here. Unresolved dynamic
dispatch, including an ambiguous trait method, stays a conservative
reject from `@rt_safe`.

## Refinement

If a dependency's public contract *refines* the one a client was last
accepted under (`effects_new ⊆ effects_old`, and the declared domain did
not move longer-lived), that client stays accepted. Only effect growth
or a move to a longer-lived (or newly declared) domain can invalidate the
prior result.

 rows (name, bits, domain; provenance is diagnostic
only). Before refinement is considered, `flowc_rt_summary_buffer_valid`
requires every serialized row to have complete `kind/name/value` NUL framing.
RT rows additionally require a bounded effect bitset and a valid lifetime
rank. Empty, truncated, malformed, or out-of-range input therefore fails
closed and can never suppress a fresh safety check.
`flowc_rt_summary_fingerprint` hashes the same valid rows.

No persistent cache currently uses the relation. Every compile checks every
imported summary. If a persistent cache is added later, it must validate the
serialized buffer before using refinement as a skip condition.

## Escape through fields and the heap

Inside a `@lifetime(D)` function, storing a reference rooted in `D` into
a longer-lived place is an error. v0 already rejected a module static.
This slice also rejects:

- a field of a longer-lived static (`holder.p = scratch`)
- a store through a `malloc` / `alloc_*` pointer (`h[0].p = scratch`)

Pointer laundering, integer round-trips, and escape through a call are
still unchecked.

## Adversarial serialization test

`tests/lang/test_rt_summary_cache_validation.flow` constructs valid and
malformed summary byte buffers directly. It covers missing terminators,
invalid bitsets/domains, empty prior state, truncated new state, and the
positive identical-contract refinement case. `tests/scripts/rt_summary.flow`
runs that fixture through `./flow test-lang` alongside the cross-module
RT/lifetime checks.

## Related

[rt-safety.md](../library/rt-safety.md) ·
[lifetime-domains.md](lifetime-domains.md) ·
[LANGUAGE_SPEC §8.4](../LANGUAGE_SPEC.md#84-lifetime-domains)
