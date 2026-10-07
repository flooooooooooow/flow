# Local region inference and automated non-aliasing proofs

> **Status:** v0 is implemented in flowc. The analysis is intraprocedural,
> annotation-free, and **fail closed**: it reports disjointness only when it
> can prove it from the function body. A wrong proof is undefined behaviour,
> so everything it cannot decide is treated as "may alias".
> Restrict / `{llvm.noalias}` emission that consumes these proofs is
> [issue #731](https://github.com/flooooooooooow/flow/issues/731).

Rust requires lifetime annotations when references alias. Flow 2.0 infers
**abstract regions** for the bindings in one function and uses that to prove
that two mutable views do not overlap. There is no region syntax and no
lifetime parameter on types.

This is the local slice of epic
[#679](https://github.com/flooooooooooow/flow/issues/679) (issue
[#694](https://github.com/flooooooooooow/flow/issues/694)). Lifetime domains
([lifetime-domains.md](lifetime-domains.md)) answer *how long* storage
lives; regions answer *which storage* a name refers to.

## What a region is

A region is an abstract storage location:

| Kind | Meaning |
|---|---|
| `LOCAL` | Fresh storage allocated in this frame. Distinct identities never alias. |
| `PARAM` | Storage bound at entry. Distinct parameters **may** alias: the caller can pass the same buffer twice. |
| `UNKNOWN` | Top. Provenance was not established (a call result, a reassignment, mixed pointer arithmetic). Aliases everything. |

Each `LOCAL` and `PARAM` region has an identity (the allocating binding).
All `UNKNOWN` regions are the same top element.

## Constraints the solver uses

The pass walks one function body and solves equality constraints, then reads
disjointness off the resulting partition.

- A parameter is a `PARAM` region. Parameters are never unified with each
  other.
- A fresh local (an array, struct, vector or scalar literal, or an
  uninitialized owned binding) is a `LOCAL` region whose identity is that
  binding.
- A copy, borrow (`&`), index, slice, field or cast **inherits** the root's
  region (equality).
- Pointer arithmetic inherits the unique referenced region: `base + off`
  shares `base`. Pure literal arithmetic (`2 + 3`) is a fresh `LOCAL`. Two
  or more referenced regions, or any unknown leaf, are `UNKNOWN`.
- A binding that is reassigned as a whole (`r = ...`) or declared more than
  once is `UNKNOWN`. An element write (`x[i] = ...`) does not retarget `x`.
- A call result is `UNKNOWN` (it may return a borrow into a parameter).

## What it proves

```flow
function f() -> i32 {
    let mut a: array<i32, 4> = [1, 2, 3, 4]
    let mut b: array<i32, 4> = [0, 0, 0, 0]
    let pa: ptr<i32> = a
    let pb: ptr<i32> = b
    for i in 0 to 4 {
        pb[i] = pa[i]
    }
    return b[0]
}
```

`a` and `b` are distinct `LOCAL` regions, so `pa` and `pb` are proven
disjoint. The C backend lowers that unit-stride copy to one `memcpy`. A local is also disjoint
from every parameter: it is allocated in this frame after the parameters
were bound.

## What it declines

```flow
function g(p: ptr<i32>, q: ptr<i32>, n: i32) -> void {
    for i in 0 to n {
        q[i] = p[i]
    }
}
```

`p` and `q` are distinct parameters, so they **may** alias. The copy stays
an ordered element loop. A `memmove` would differ from the loop when
`q == p + 1`, because the loop propagates each write forward. The same decline applies to two views of one local, a
reassigned binding, and a value whose provenance is a call.

Pointer arithmetic is not a fresh region:

```flow
function h(base: ptr<i32>, n: i32) -> i32 {
    let p: ptr<i32> = base + 0
    let q: ptr<i32> = base + n
    return p[0] + q[0]
}
```

`p` and `q` inherit `base`. They are not restrict candidates.

## Diagnostics

When aliasing cannot be proven safe at a call that passes two
pointer or span arguments rooted in the **same** region, or when at least
one argument has unknown provenance, flowc can name the call:

```text
error: cannot prove that arguments of 'take' do not alias; they are rooted
       in the same region (overlapping mutable access is not shown to be
       safe) at line 11, column 12
```

This check is opt-in: set `FLOWC_REGION_CHECK=1`. Two distinct parameters
stay silent. That is the expected fail-closed answer.

`FLOWC_REGION_REPORT=1` writes per-binding remarks into the generated C:

```c
/* region[local]: `a` */
/* region[restrict-candidate]: `a` */
/* region: disjoint */
memcpy((void*)(&(pb)[0]), (void*)(&(pa)[0]), ...);
```

A **restrict candidate** is a local whose `LOCAL` region is unique in the
function: disjoint from every parameter and from every other tracked
binding. That is the sound subset a backend may annotate `restrict` on a
local pointer ([#731](https://github.com/flooooooooooow/flow/issues/731)).
This pass never claims two *parameters* are disjoint by itself; that needs
call-site evidence.

## What this does not do

- Interprocedural proofs that two parameters are disjoint, except as
  consumed later by the #731 call-site certificate.
- Interval disjointness of overlapping slices of one array (`a[0..2]` vs
  `a[2..4]`). Same-root views are "may alias" here; #731's view analysis
  covers constant non-overlapping slices for restrict emission.
- Provenance through struct fields other than the root object, closures,
  or a call that launders a pointer.
- Region variables in the type system or source syntax.

Those gaps are fail closed: the analysis reports "may alias" rather than a
proof.

## Related

[Lifetime domains](lifetime-domains.md) · [Spans](spans.md) ·
[Memory](../library/memory.md) ·
[LANGUAGE_SPEC §8.5](../LANGUAGE_SPEC.md#85-local-region-inference)

Tests: `tests/lang/test_region_inference.flow`,
`tests/cgen/region_inference.flow`, `tests/cgen/region_unproven.flow`.
The flowc selftest (`region_ok=1`) pins the Python prototype's cases.
