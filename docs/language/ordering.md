# Declarative Ordering

Sorting in FLOW is an **intent** surface, not an algorithm call.

```flow
xs |> sort
xs |> sort by .score
xs |> sortBy [desc .score, asc .name]
```

The compiler chooses how to realize the order (Phase 1: stable insertion sort on fixed-size arrays).

## Phase 1 (shipped)

| Form | Meaning |
|------|---------|
| `xs \|\> sort` | Ascending order of elements (numeric / string) |
| `xs \|\> sort descending` | Reverse whole-element order |
| `xs \|\> sort unique` | Sort, then compact adjacent duplicates to the front |
| `xs \|\> sort by .field` | Order struct array by one field (asc) |
| `xs \|\> sort by [desc .a, asc .b]` | Lexicographic multi-key |
| `xs \|\> sortBy [...]` | Alias for `sort by [...]` |
| `stable` / `unstable` | Stability preference (Phase 1 always uses insertion = stable) |
| `with entropy` / `with entropy(seed: N)` | Parsed; reserved for randomized strategies |
| `parallel`, `adaptive`, `gpu`, … | Parsed as policies; not specialized yet |

Semantics today:

- **In-place** on `array<T, N>` (same storage; expression yields the array)
- Struct elements require `by` / `sortBy` with scalar or string fields
- `unique` compactsthe prefix; the fixed size `N` does not shrink (tail is stale)

See `examples/basics/declarative_sort.flow`.

## Later (PRD)

Adaptive algorithm selection, GPU/SIMD/distributed backends, entropy as a first-class effect, `order { }` blocks, composable primitives (`split` / `partition` / `merge`), latency/memory objectives (`sort under 2ms`). Tracked in [`docs/project/Questions.md`](../project/Questions.md).
