# Multi-implementation selection (#147)

Flow separates intent from implementation. A declarative construct names
what must hold. The compiler picks the cheapest implementation that
satisfies the constraints at the call site.

## How it works

Three pieces:

1. **Facts** (`PlanFacts` in `compiler/src/sort_plans.flow`): what the
   compiler knows at one site. Element count, type, ordering provenance,
   policies.
2. **Implementation**: one lowering. Declares an applicability check, a cost
   model, and a scratch claim.
3. **Selector** (`flowc_plan_select`): runs every implementation for the
   construct, picks the cheapest applicable one, and records why every other
   candidate lost.

The record is the point. `flow explain` prints it verbatim.

## Constructs

### sort

Six lowerings, from no-op (input already ordered) to stable bottom-up
merge. See `docs/language/ordering.md`.

### search

Two lowerings: linear scan and binary search. Binary search wins when
ordering provenance proves the array is ascending.

### matmul

Cost models only (`compiler/src/general_plans.flow`); no lowering consults
them yet. Two lowerings:

| Implementation | When it wins | Scratch |
|---------------|-------------|---------|
| naive | n < 64 (fits in L1) | 0 |
| blocked | n >= 64 (cache tiling) | 8 KiB |

`require(memory < 4096)` flips a large matmul back to naive.

### reduce

Cost models only, as for matmul. Two lowerings:

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

Parsed by `compiler/src/constraints.flow`. Becomes the fact
`require_memory_bytes = 4096`, which the matmul and reduce applicability
checks read.

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

```flow-future
@require(memory < 4096)
@prefer(parallel)
let result = xs |> reduce(sum)
```

The parser is in `compiler/src/constraints.flow`. It is not yet wired into
the compiler, and neither was the Python original. Sort and search take no
`require` / `prefer` today; their constraints are the policies `general`,
`adaptive`, `unique` and `unstable`, and the scratch budget. Wiring the
attribute form is a follow-up once the cost IR has real units.

## Adding a new construct

1. Add the plan codes, checks, costs and scratch claims to
   `compiler/src/sort_plans.flow` (or a sibling module).
2. Build the facts at the call site in cgen.
3. Call `flowc_plan_select` and emit the C body for the chosen plan.
4. Pass the report buffer when `FLOWC_EXPLAIN=1` so `flow explain` prints
   the record.

See `flowc_cgen_emit_sort_by` and `flowc_cgen_emit_pipe_find` in
`compiler/src/cgen.flow` for the sort/search example, and
`compiler/src/general_plans.flow` for the matmul/reduce cost models.

## Cost model

Costs are estimated element operations, a dimensionless count. They are
static estimates from an annotated model, never measurements. Two costs
are comparable within one construct and meaningless across constructs.

The cost IR has one dimension today. Real units (cycles, joules, bytes)
need a target model. That is future work.
