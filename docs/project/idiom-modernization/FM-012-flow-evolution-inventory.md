# FM-012 slice 1: flow/evolution equation syntax inventory

Status: evidence inventory for [#1740](https://github.com/flooooooooooow/flow/issues/1740), base `9e96fa1d3` (post #1736). This is a discovery document. It does not approve semantics, assign feature status, or complete FM-012. It covers the flow-block equation forms evidenced in the source and tests named below. Anything absent from this slice is `unverified` or out of scope.

## Scope and non-scope

**In scope (this slice):**

| Construct | Surface form (as evidenced) |
|---|---|
| Flow declaration | `flow Name { ... }` block containing time/state declarations and equation-like members |
| Continuous evolution | `<state> evolves as <expr>` |
| Solver declaration | `solver { dt <duration> method <name> }` with `dt` and `method` items (evidenced: `euler`, `rk4`) |
| Discrete periodic update | `every <duration> { <becomes-updates> }` and its interaction with continuous states in fixtures/tests |

**Out of scope for this slice:**

- Dynamics DSL forms (e.g. `d/dt`, `∂/∂x`, equation blocks lowered by `compiler/src/dynamics_dsl.flow` and covered by `compiler/fixtures/dynamics_dsl/` / `compiler/scripts/parity_dynamics_dsl.flow`) belong to a separate FM-012 slice.
- Hybrid/event forms in full (`when ... reaches ...`, `always`/`never`/`guarantee`, `recognize`, `connect`, nested flow composition) except where a fixture/test is cited as interaction evidence.
- Unit-member derivative semantics and unit erasure/coercion across evolution are semantics-gated work for FM-010 and FM-011.
- Algebraic constraints/DAE, boundary conditions, typed symbolic PDE.
- MLIR lowering of these forms in `compiler/src/mlirgen.flow` / bundle emission stays `unverified` here; only the flow-block lowering/parity path is cited.

## Parse and lowering owners

| Stage | Evidence anchor | Notes |
|---|---|---|
| Parser (flow items) | `compiler/src/parser.flow` ~5047–5145: parses `<ident> evolves as <expr>` as `FLOW_ITEM_EVOLVES`; parses `every <duration> { becomes... }` as `FLOW_ITEM_EVERY`; parses `solver { dt <duration> method <ident> }` as `FLOW_ITEM_SOLVER` (accepts `dt`/`method` items, rejects other idents / missing ident). `when ... reaches ...` parsing is adjacent in the same region and remains outside this slice. | Exact token/kind names and full grammar are the source of truth; this row records observed anchors only. |
| Flow-block lowering / semantic checks | `compiler/src/flow_blocks.flow` (module header states lowering for `flow` blocks: `evolves`, `when`, `every`, `solver`, `always`/`never`, `recognize`, `connect`, nested flows, `\|>` pipelines). `evolves` handled at ~2546 and validated at ~3777–3815: target must be a declared state, exactly one `evolves` per state, RHS checked pure in the `'x evolves as'` context. `solver`/`every` validation and codegen paths exist in the same module (line citations left partial here). | Lowering emits Flow source before parse (per parity gate header), so parity is stated over parsed declarations/expansion, diagnostics and run output. |
| Math/prose bridge | `compiler/src/math_prose.flow` exists in the work package scope; this slice read only its module header, so its relation to flow-block equation spelling stays `unverified`. |

## Parity and verification surfaces

| Surface | Command / path | What it evidences (per source) | Status in this slice |
|---|---|---|---|
| Flow-block parity gate | `compiler/scripts/parity_flow_blocks.flow` (`FIX=compiler/fixtures/flow_blocks`, `WORK=compiler/build/parity_flow_blocks`) | Flow-port lowering parity against Python host behavior: `ok_*.flow` expansion vs `.expected`, `err_*.flow` diagnostics vs `.error`, `run_*.flow` build/run stdout+exit+stderr vs `.out`; passthrough of tracked `.flow` without a flow block; optional tree check against Python at a given rev (`--python <rev>`, header notes last Python rev `7527ab37`); example e2e `examples/evolution/bouncing_ball_evolves.flow`. | Documented from script header/source; this docs-only slice did not execute it. |
| Cgen/language tests | `tests/lang/test_time_blocks.flow`, `tests/lang/test_time_blocks_rk4.flow` | End-to-end compiled behavior (see below). | Documented from file contents at this revision; this slice records existing evidence only. |

## Construct inventory (evidenced)

### `evolves as` (continuous state derivative)

- **Syntax/evidence:** `<state_name> evolves as <expr>` parsed in `compiler/src/parser.flow` ~5048–5070 as `FLOW_ITEM_EVOLVES(rhs)`. Lowered/checked in `compiler/src/flow_blocks.flow` around ~2546 (parse/lower) and ~3786–3806 (state must exist, single derivative, pure RHS).
- **Positive anchors:** `tests/lang/test_time_blocks.flow` declares `t evolves as 1.0`; `tests/lang/test_time_blocks_rk4.flow` declares `x evolves as v`, `v evolves as 0.0 - x` and `x evolves as 1.0`. Fixtures under `compiler/fixtures/flow_blocks/` that contain `evolves as` include `ok_basic.flow` (`:5-6`), `run_features.flow` (several flows and states) and `ok_rk4_f32.flow`.
- **Negative anchors (diagnostics/constraints):** `err_evolves_twice.error` says "state 'x' in flow 'Osc' has two 'evolves' declarations; a state has exactly one derivative"; `err_evolves_unknown.error/.flow` present; `err_lambda.error` says "lambda in 'x evolves as' of flow 'Osc' is not supported"; `err_impure_nested.error` reports that a call in `'x evolves as'` cannot be proven pure (v1); `err_every_evolved.error/.flow` present (per fixture naming/flow-block validation intent, a state with `evolves` conflicts with that discrete-driving form; exact message omitted here). `err_reset_unknown.flow` also contains `evolves`. Fixture set is the authoritative negative corpus.
- **Semantic classification:** parsed and lowered in the flow-block pipeline; end-to-end behavior evidenced by `tests/lang` and parity gate fixtures. Unit-carrying derivative typing is a separate, semantics-gated question (FM-010) left for that work.

### `solver { dt ... method ... }`

- **Syntax/evidence:** `compiler/src/parser.flow` ~5107–5138 parses `solver { ... }` with `dt <duration>` and `method <ident>` items into `FLOW_ITEM_SOLVER`.
- **Positive anchors:** `tests/lang/test_time_blocks.flow` declares `solver { dt 1 ms  method euler }` and checks that `Counter_default_dt()` equals `0.001`; `tests/lang/test_time_blocks_rk4.flow` declares `solver { dt 1 ms  method rk4 }`.
- **Negative anchors:** fixtures `err_solver_dt_twice`, `err_solver_item`, `err_solver_method_twice`, `err_solver_method`, `err_solver_no_dt`, `err_solver_zero`, `err_two_solvers` (`.flow`/`.error` pairs under `compiler/fixtures/flow_blocks/`).
- **Semantic classification:** solver selection and default `dt` are part of the flow-block model as exercised by tests/fixtures. The precise numerical contract beyond these tests (tolerance, multi-method support beyond `euler`/`rk4`, target parity) is `unverified` in this slice.

### `every <duration> { ... }` (discrete periodic block)

- **Syntax/evidence:** `compiler/src/parser.flow` ~5088–5105 parses `every <duration> { becomes... }` as `FLOW_ITEM_EVERY` (duration must parse; body is a becomes-body). Lowering/validation present in `compiler/src/flow_blocks.flow` (e.g. period handling around ~2580+ region, discrete/continuous conflict checks around ~3939+).
- **Positive anchors:** `tests/lang/test_time_blocks.flow` shows `every 10 ms { ticks becomes ticks + 1.0 }` firing 100 times over 1000 steps of 1ms, catching up nine firings after one 95ms step, and `every 10 ms { a becomes b; b becomes a }` applying simultaneous writes. The fixture `ok_every_when.flow` with its `.expected` golden is present.
- **Negative anchors:** fixtures `err_every_evolved`, `err_every_twice`, `err_every_unknown`, `err_every_zero` (`.flow`/`.error` pairs). (No `err_every_empty` file observed in the sampled prefix; the negative corpus is the fixture directory.)
- **Semantic classification:** parsed, lowered and behaviorally tested for the cases above. Interaction rules with all event/state forms are `unverified` beyond cited fixtures.

## Open / unverified items

- The exact C/MLIR code generation shape for `evolves`/RK4 stepping, and how `dt`/method are represented downstream, stay `unverified`.
- Dynamics DSL equation spelling (`d/dt`, derivatives, algebraic equations) is out of scope, since it uses a different lowering path, fixtures and gate.
- Whether `method` accepts names beyond those evidenced (`euler`, `rk4`) and the failure mode: fixture `err_solver_method` exists but was unopened in this slice; treat as `unverified` here beyond "invalid/unsupported method is diagnosed".
- Unit-typed evolution correctness and coercion behavior are deferred to FM-010.
- Completeness of this inventory relative to all flow-block equation-like forms: this initial slice is partial.

## Verification performed for this slice

- Evidence gathered by reading the source/test/fixture paths cited above at `9e96fa1d3`.
- No `compiler/src/` or generated files changed.
- Planned repo gates before PR: `./flow tool doc_links`, `./flow tool script_refs` (docs-only change).

