# Explainable compilation

Some Flow constructs say what must hold rather than how to get there.
`xs |> sort` asks for an order. `xs |> find(t)` asks for an index. The
compiler decides which C loop to emit, and that decision depends on facts a
reader of the source cannot see: how large the array is, what the element
type bounds the keys to, whether an earlier statement already left the array
sorted.

A decision like that is only trustworthy if you can look at it.

```
./flow explain program.flow
```

or, through the transpiler directly:

```
python3 -m flow.transpiler program.flow --c --strict --explain -o out.c
```

The report goes to stderr, so it does not mix with generated output.

## What it prints

One block per selection site, in emission order.

```
Compilation plan for tests/lang/test_sort_plans.flow
====================================================

[5] sort at line 100 in main()
      array<u8, 1024> keys: whole element; order: asc
      facts: n=1024, direction=asc, elem=u8, elem_bytes=1, elem_kind=int,
             expect_runs=unknown, input_order=unknown, key_range=[0, 255],
             keys=0, stable=True

      already_ordered           --   rejected: input is not proven to be in asc order (provenance: unknown)
      reverse_in_place          --   rejected: input is not proven to be in strictly desc order (provenance: unknown); reversing a run of equal keys would break stability
   -> counting                2560   CHOSEN
                                     stable counting sort over a proven non-negative bounded key range
      insertion           2.62e+05   ok
                                     stable in-place insertion sort; no scratch, wins for small n
      natural_merge          10240   ok
                                     run-detecting stable merge; one pass finds ascending and descending runs, then merges them pairwise
      bottom_up_merge        11264   ok
                                     stable bottom-up merge sort; the general-purpose plan

      chose counting: cheapest applicable plan: 2560 vs 10240 for natural_merge (75% less work)

Costs are estimated element operations from a static model, not measurements.
```

Reading it top to bottom:

- **The site.** Construct, source line, enclosing function.
- **The shape.** Element type, length, keys, direction, policies.
- **The facts.** Everything the selector was given. `input_order` and
  `key_range` are the ordering hints; see
  [Declarative Ordering](ordering.md).
- **Every candidate.** Applicable ones show their cost and their one-line
  summary. Rejected ones show the constraint they failed, in words, with the
  fact that made it fail.
- **The choice**, with the margin over the runner-up.

Costs are estimated element operations from an annotated model. They are
comparable within one construct and meaningless across constructs, and they
are never measurements. The report says so on every run so nobody quotes
them as timings.

## Failed budgets

Some rejections are not about the data but about resources. Compiler-
introduced scratch is capped, because a merge plan puts its buffer on the C
stack. When that cap bites, the report says which budget, by how much, and
what could be changed:

```
[1] sort at line 8 in main()
      array<f64, 65536> keys: whole element; order: asc
      facts: n=65536, direction=asc, elem=f64, elem_bytes=8, elem_kind=float, ...

      already_ordered           --   rejected: input is not proven to be in asc order (provenance: unknown)
      reverse_in_place          --   rejected: input is not proven to be in strictly desc order (provenance: unknown); reversing a run of equal keys would break stability
      counting                  --   rejected: element type is float, not a bounded integer
   -> insertion           1.07e+09   CHOSEN
                                     stable in-place insertion sort; no scratch, wins for small n
      natural_merge             --   rejected: scratch 512.0 KiB exceeds the 256.0 KiB compiler scratch budget
      bottom_up_merge           --   rejected: scratch 512.0 KiB exceeds the 256.0 KiB compiler scratch budget

      chose insertion: only applicable implementation

      possible resolutions
        - natural_merge: the merge buffer is one element per input element; sort in chunks that fit the scratch budget, or use a narrower element type
        - bottom_up_merge: the merge buffer is one element per input element; sort in chunks that fit the scratch budget, or use a narrower element type
        - already_ordered: sort where the order is provable. A call taking the array, a write to one of its elements, or a surrounding loop all drop the fact.
```

That site fell all the way back to an O(n²) insertion sort on 65536 elements,
and the report is where you find out. Resolutions appear only when the
selector was actually boxed in, either by a budget or by having one candidate
left standing. An ordinary rejection already explains itself on its own line.

## How a construct joins in

`src/flow/plan_selector.py` is construct-agnostic. Registering an
implementation takes four things: when it applies, what it costs, what
scratch it claims, and what a programmer could change if it is refused.

```python
register(
    Implementation(
        name="binary_search",
        construct="search",
        summary="lower-bound binary search; provenance proves the array is ascending",
        applicable=lambda f: (
            None
            if f.get("input_order", "unknown").startswith("asc")
            else f"input is not proven to be in ascending order "
                 f"(provenance: {f.get('input_order')})"
        ),
        cost=lambda f: math.log2(max(2.0, float(f.n))),
        rank=0,
        resolution="sort the array immediately before searching it",
    )
)
```

The applicability predicate returns `None` to mean yes, and otherwise the
sentence the report prints. Writing the rejection as a sentence rather than a
boolean is the whole design: a constraint that cannot explain itself is not
worth having.

`select(facts, location, detail)` then runs every implementation for the
construct, applies the scratch budget, keeps the cheapest survivor, and
returns a record of all of it. The C generator appends each record to
`self._selections`, and `flow_to_c` exposes the list as
`flow_to_c.last_selections`.

Two constructs use this today, `sort` and `search`, both in
`src/flow/ordering_plans.py`. They deliberately share facts: `input_order` is
produced by the ordering-hints pass for `sort` and consumed by `search`.

## Scope

This covers implementation selection for declarative constructs. It does not
yet cover buffer or arena placement, worst-case latency estimates, or heap
operations remaining inside real-time regions, which is where issue #146
eventually points. `flow verify --explain` remains a separate thing: it
prints proof traces, not plans.

## See also

- [Declarative Ordering](ordering.md) for the plans and hints themselves
- `benchmarks/ordering/RESULTS.md` for measured numbers behind the cost models
- `tests/unit/test_plan_selector.py` for the selector's contract
