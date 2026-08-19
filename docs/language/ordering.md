# Declarative Ordering

Sorting in FLOW is an **intent** surface, not an algorithm call.

```text
xs |> sort
xs |> sort by .score
xs |> sortBy [desc .score, asc .name]
xs |> find(target)
```

You say what must hold. The compiler picks how to realize it, from a registry
of implementations with cost models, and `--explain` prints the choice. See
[Explainable compilation](explainable-compilation.md).

## Surface

| Form | Meaning |
|------|---------|
| `xs \|\> sort` | Ascending order of elements (numeric / string) |
| `xs \|\> sort descending` | Reverse whole-element order |
| `xs \|\> sort unique` | Sort, then compact adjacent duplicates to the front |
| `xs \|\> sort by .field` | Order struct array by one field (asc) |
| `xs \|\> sort by [desc .a, asc .b]` | Lexicographic multi-key |
| `xs \|\> sortBy [...]` | Alias for `sort by [...]` |
| `stable` / `unstable` | Stability preference (every plan is stable today) |
| `adaptive` | Assert the input has structure; shifts the run estimate |
| `general` | Pin the general plan and ignore every hint |
| `xs \|\> find(t)` | Index of the first element equal to `t`, or `-1` |
| `with entropy` / `with entropy(seed: N)` | Parsed; reserved for randomized strategies |
| `parallel`, `gpu`, `simd`, … | Parsed as policies; not specialized yet |

Semantics:

- **In-place** on `array<T, N>` (same storage; expression yields the array)
- Struct elements require `by` / `sortBy` with scalar or string fields
- `unique` compacts the prefix; the fixed size `N` does not shrink (tail is stale)
- `find` takes a scalar or string array and yields an `i32` index

See `examples/basics/declarative_sort.flow`, `tests/lang/test_sort_plans.flow`.

## Float ordering: IEEE 754 totalOrder

A comparator has to be a total order or a sort is undefined. C's `<` on
floats is not one: NaN compares false against everything, so a comparator
built from `<` and `>` reports "equal" for every pair involving a NaN, and
that relation is not transitive. Before this was fixed,
`[3.0, NaN, 1.0, NaN, 2.0] |> sort` came back as `3 NaN 1 NaN 2`, with the
finite values never ordered.

Declarative ordering therefore compares floats with **IEEE 754-2008
totalOrder**:

```
-NaN < -inf < ... < -1.0 < -0.0 < +0.0 < +1.0 < ... < +inf < +NaN
```

Concretely:

- Negative NaNs sort before everything, positive NaNs after everything.
- Among NaNs of the same sign, the order is by payload bits. Positive NaNs
  ascend by payload; negative NaNs descend, which is what totalOrder
  specifies.
- `-0.0` sorts strictly before `+0.0`.
- The relation is reflexive, antisymmetric and transitive for every pair of
  bit patterns, which is what a sort needs from a comparator.

The implementation is a bit trick, not a chain of branches: the sign-magnitude
bit pattern is mapped onto an unsigned integer whose numeric order is the total
order, then the two integers are compared. It is a load, an xor, and a compare
per element (`__flow_ord_key_f64` in the generated C).

### Why totalOrder and not NaN-last

Three options were on the table.

**Reject NaN at runtime.** Costs a branch per comparison and turns ordering
into an operation that can abort. Flow's ordering is used inside dynamics and
evolution steps where a NaN is a diagnostic, not a reason to kill the process.

**NaN-last.** Simpler to explain, and it is what several languages do. It
still needs an invented rule for the sign of NaN and another for `-0.0`
against `+0.0`, and those rules would be Flow's alone.

**totalOrder.** Already specified, by IEEE 754-2008 clause 5.10, so there is
nothing to invent and nothing to argue about. It orders every bit pattern,
including NaN payloads, which makes `sort` a deterministic function of the
input bits. It is one xor more expensive than a raw compare.

The cost of totalOrder is that it splits NaNs by sign, so a program that
produced both `-NaN` and `+NaN` finds them at opposite ends. That is a fair
price for a rule taken from the standard rather than made up.

### Arithmetic is untouched

`<`, `>`, `<=`, `>=` and `==` on `f32` / `f64` keep IEEE semantics. `NaN == NaN`
is false. `NaN < 1.0` is false. `-0.0 == 0.0` is true. Nothing about the
ordering change affects arithmetic; the split is deliberate, and is the same
split array languages draw between IEEE comparison and high-level match.

The one place the two meet is `sort unique`, which compacts elements that the
**ordering** calls equal. For floats that means bitwise equality, so two NaNs
with the same payload collapse to one, and `-0.0` and `+0.0` both survive.

`tests/lang/test_sort_nan.flow` pins all of this.

## Plans

The compiler chooses among six sort lowerings. Each declares when it applies,
how much scratch it needs, and what it costs; the cheapest applicable one
wins. `src/flow/ordering_plans.py` holds the declarations.

| Plan | Applies when | Cost model |
|------|--------------|-----------|
| `already_ordered` | Provenance proves the input is in the requested order, no `unique` | 0 |
| `reverse_in_place` | Provenance proves it is *strictly* reversed | n/2 |
| `counting` | Whole-element integer key with a proven non-negative range of at most 4096 | 2n + 2k |
| `insertion` | Always (unless pinned) | n²/4, or n when the input is known ordered |
| `natural_merge` | n ≥ 16, scratch fits | n + extension + n·log2(runs) |
| `bottom_up_merge` | Always (unless pinned) | n + n·log2(n) |

Every plan is stable. `reverse_in_place` needs a *strict* reversal precisely
because reversing a run of equal keys would not be.

Compiler-introduced scratch is capped at 256 KiB, because the merge plans put
their buffer on the C stack. Past that they are rejected and insertion takes
over. `--explain` names the budget when that happens.

Search has two lowerings on the same machinery:

| Plan | Applies when | Cost model |
|------|--------------|-----------|
| `binary_search` | Provenance proves the array is ascending | log2(n) |
| `linear_scan` | Always | n/2 |

## Hints

Two kinds of fact reach the selector.

**From the type.** A `u8` array bounds every key to `[0, 255]`, a `bool` array
to `[0, 1]`. That is enough for the counting plan with no analysis at all.

**From provenance.** `src/flow/ordering_hints.py` walks a function body in
source order and tracks, per array variable, the order it is known to be in
and the integer range of its elements. Two things create a fact: an array
literal whose elements are all numeric literals, and a `|> sort` in
straight-line code. Facts are dropped on any assignment to the variable or one
of its elements, on the variable being passed to a call, and on anything
inside a loop, conditional or match arm. The pass never guesses: a missed hint
costs a general plan, a wrong hint skips a sort that was needed.

The cross-construct case is the point of carrying them:

```text
xs |> sort            # xs is now provably ascending
let i = xs |> find(t) # so this is a binary search, not a scan
```

Insert a call taking `xs` between those two lines and the fact is gone, the
search drops back to a linear scan, and `--explain` says why.

## Measured

`benchmarks/ordering/RESULTS.md` has the numbers. On an Apple M4 Max at 32768
elements, against the pinned general plan: 39x on already-sorted input, 28x on
reverse-sorted, 1.2 to 1.3x on partially ordered and random input, and 47x for
the counting plan on `u8`.

## Later (PRD)

GPU / SIMD / distributed backends, entropy as a first-class effect, `order { }`
blocks, composable primitives (`split` / `partition` / `merge`), latency and
memory objectives (`sort under 2ms`). Tracked in `Questions.md`.
