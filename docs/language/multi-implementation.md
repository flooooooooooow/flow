# Multi-implementation selection (#147)

Flow separates intent from implementation. A declarative construct names
what must hold. The compiler picks the cheapest implementation that
satisfies the constraints at the call site.

## How it works

Three pieces:

1. **Facts** (`plan_selector.py`): what the compiler knows at one site.
   Element count, type, ordering provenance, constraints.
2. **Implementation** (`plan_selector.py`): one lowering. Declares an
   applicability predicate, a cost model, and a scratch claim.
3. **Registry** (`ordering_plans.py`, `general_plans.py`): each construct
   registers its implementations. The selector picks the cheapest
   applicable one and records why every other candidate lost.

The record is the point. `--explain` prints it verbatim.

## Constructs

### sort

Six lowerings, from no-op (input already ordered) to stable bottom-up
merge. See `docs/language/ordering.md`.

### search

Two lowerings: linear scan and binary search. Binary search wins when
ordering provenance proves the array is ascending.

### matmul

Two lowerings:

| Implementation | When it wins | Scratch |
|---------------|-------------|---------|
| naive | n < 64 (fits in L1) | 0 |
| blocked | n >= 64 (cache tiling) | 8 KiB |

`require(memory < 4096)` flips a large matmul back to naive.

### reduce

Two lowerings:

| Implementation | When it wins | Scratch |
|---------------|-------------|---------|
| sequential | n < 1024 | 0 |
| parallel_tree | n >= 1024 or `prefer(parallel)` | n * elem_bytes |

`prefer(parallel)` flips a small reduce to the tree.

## Constraint vocabulary

### require (hard)

Rejects implementations that cannot meet the budget.

```
require(memory < 4096)     # reject implementations needing > 4 KiB scratch
require(scratch <= 8192)   # same, explicit name
require(latency < 1000)    # reject implementations with cost > 1000
```

Parsed by `src/flow/constraints.py`. Becomes entries in the Facts data
dict: `require_memory_bytes = 4096`. Implementations check these in their
applicability predicates.

### prefer (soft)

Biases the cost model toward an objective.

```
prefer(parallel)    # pick parallel-friendly implementations
prefer(latency)     # minimise latency (parsed, not yet wired)
prefer(energy)      # minimise energy (parsed, not yet wired)
prefer(memory)      # minimise memory (parsed, not yet wired)
```

Only `prefer(parallel)` affects the cost model today. The others are
parsed for forward compatibility.

## Surface syntax (future)

The attribute form is the target syntax:

```
@require(memory < 4096)
@prefer(parallel)
let result = xs |> reduce(sum)
```

The parser is in `constraints.py`. It is not yet wired into the compiler.
Today the compiler builds Facts programmatically. Wiring the attribute
form is a follow-up once the cost IR has real units.

## Adding a new construct

1. Create implementations in a new `*_plans.py` module.
2. Register each with `register(Implementation(...))`.
3. Add facts at the call site in the C generator (or MLIR generator).
4. Call `select(facts, location, detail)` and use `sel.chosen` to pick
   the C body.
5. Append the `Selection` to `self._selections` so `--explain` prints it.

See `ordering_plans.py` for the sort/search example. See
`general_plans.py` for the matmul/reduce example.

## Cost model

Costs are estimated element operations, a dimensionless count. They are
static estimates from an annotated model, never measurements. Two costs
are comparable within one construct and meaningless across constructs.

The cost IR has one dimension today. Real units (cycles, joules, bytes)
need a target model. That is future work.
