# Feature and ownership coverage: complete inventory schema

This map tells agents where to look. It does not certify that every named construct is fully supported. Treat feature maturity, targets and compiler version as unknown until tested on the actual checkout. `work-packages.json` is the work queue; a generated registry (FM-003/004) must become the source of truth for support claims.

| Feature family | Primary implementation | Semantic/negative evidence | Canonical teaching and consumers |
| --- | --- | --- | --- |
| Lexer, grammar, operators, contextual keywords | `compiler/src/lexer.flow`, `token.flow`, `parser.flow`, `ast.flow` | `compiler/fixtures/`, `tests/lang/`, parser coverage | `docs/grammar.ebnf`, `docs/language/syntax.md`, tree-sitter |
| Type inference, generics, overloads and distinct types | `compiler/src/sem_check.flow`, `sem_types.flow`, `overload*.flow` | `compiler/fixtures/typecheck_rules/`, `tests/lang/` | `docs/language/types.md`, `docs/book/` |
| Units, dimension vectors, casts and quantity literals | `compiler/src/sem_check.flow`, `sem_types.flow`, `flow_blocks.flow` | `compiler/fixtures/units_*.flow`, `tests/cgen/flow_dimensioned_state_pendulum.flow` | `lib/stdlib/units_si.flow`, `examples/evolution/units_kinematics.flow` |
| Continuous state, `evolves as`, generated Euler/RK4 | `compiler/src/flow_blocks.flow` | `compiler/fixtures/flow_blocks/`, `compiler/scripts/parity_flow_blocks.flow` | `examples/evolution/pendulum_evolves.flow`, `docs/tutorials/evolution.md` |
| Periodic time, `every`, `becomes`, solver configuration | `compiler/src/flow_blocks.flow` | `compiler/fixtures/flow_blocks/`, `tests/lang/` | `examples/evolution/thermostat_evolves.flow` |
| Events, invariants, `when`, `always`, `never`, `guarantee` | `compiler/src/flow_blocks.flow` | `compiler/fixtures/flow_blocks/run_guarantee.flow`, event fixtures | `examples/evolution/bouncing_ball_evolves.flow`, `docs/book/13-evolution-and-dynamics.md` |
| Nested flow and typed `connect` | `compiler/src/flow_blocks.flow` | `compiler/fixtures/flow_blocks/err_connect_*.flow` | `examples/evolution/robot_connect.flow`, `flow-idiomatics` |
| State-space control, `dsys`, `sense`, `analyze`, `represent` | `compiler/src/dynamics_dsl.flow` | `compiler/fixtures/dynamics_dsl/`, `compiler/scripts/parity_dynamics_dsl.flow` | `lib/stdlib/dynamics/`, `examples/evolution/pendulum_represent_linear.flow` |
| Fields, `laplacian`, boundary and spatial solver | `compiler/src/field_dsl.flow`, `field_dsl_core.flow` | `compiler/fixtures/field_dsl/`, `tests/lang/test_field_dsl_core.flow` | `examples/evolution/heat_diffusion.flow`, `lib/stdlib/dynamics/pde.flow` |
| Typed science/PDE DAG, Sofia-class solver | `lib/stdlib/science/`; PR #1703 experimental builder | `tests/lang/test_sofia_*.flow` as available; validate PR state | `examples/science/sofia/`, `docs/project/Questions.md` |
| Physics and geometry DSL | `compiler/src/physics_dsl.flow`, geometry modules | `tests/lang/test_physics_dsl_port.flow` | `docs/language/physics-dsl.md`, examples |
| Equation expressions and math prose | `compiler/src/parser.flow`, `expr_type.flow`, `math_prose.flow` | `compiler/scripts/smoke_math_prose.flow`, `tests/lang/test_math_prose_coord.flow` | `docs/language/functions.md`, `examples/compilers/math_prose_expr_demo.flow` |
| Dual/Tensor and autodiff | `compiler/src/expr_type.flow`, C lowering and `lib/stdlib/autodiff*.flow` | `tests/cgen/dual_ops_sugar.flow`, grad-check examples | `examples/ml/autodiff/`, `docs/library/autodiff-guide.md` |
| Effects, capability implementations, nested handlers, effect rows | `compiler/src/effects.flow`, `sem_check.flow` | `compiler/fixtures/effects/`, `compiler/scripts/parity_effects.flow` | `docs/effects-showcase.md`, `examples/effects/effect_rows.flow` |
| Concurrency, async/fibers and cancellation | runtime and `lib/stdlib/` modules, compiler effects paths | `tests/runtime/`, `examples/concurrency/` | `docs/language/async-effects.md`, `docs/book/12-effects-and-concurrency.md` |
| Span/borrow/lifetime, `@rt_safe`, transitive effects | `compiler/src/sem_check.flow`, `rt_summary.flow`, `wcet.flow` | `compiler/fixtures/rt_summary/`, RT rules | `examples/audio/rt_safe_callback.flow`, `docs/language/rt-summaries.md` |
| Higher-order functions, closures, `match` | parser/typechecker, `compiler/src/mono_*.flow` | `tests/lang/`, `compiler/fixtures/mlir/` | `examples/generics_traits/`, `flow-idiomatics` |
| Pipes, fork, choose and fusion | `compiler/src/parser.flow`, `pipeline_fusion.flow` | `compiler/fixtures/choose_uninferrable.flow`, `tests/lang/` | `examples/basics/pipeline_*.flow` |
| Sort/search planning and cost constraints | `compiler/src/sort_plans.flow`, `general_plans.flow`, `constraints.flow` | `tests/lang/` and planning fixtures | `docs/language/ordering.md`, `docs/language/multi-implementation.md` |
| C/MLIR/WASM/JS/GPU codegen and parity | `compiler/src/cgen.flow`, `mlirgen.flow`, `wasm_gen.flow`, shader/GPU emitters | `compiler/mlir_vs_c/`, `tests/gpu/`, target CI | `docs/project/vgpu-parity.md`, `flow-idiomatics/BACKEND_PARITY.md` |
| Format, LSP, code actions, idiom diagnostics | `compiler/src/fmt.flow`, `lsp_*.flow`, `tools/check/main.flow`, `tools/lsp/` | `tests/check/`, `tests/tools/lsp/` | `docs/DEVELOPMENT.md`, `docs/idiomatic-flow.md`, external editor grammars |
| Docs, visualization, browser and lesson routing | `tools/doc_examples/`, `scripts/tools/build_wiki/`, `site/` | `tests/doc_examples/`, `scripts/check_live_demos.mjs` | `docs/tutorials/`, `docs/book/`, `docs/playground/` |
| Recognitional/verification and proof-specific notation | `compiler/src/recognition*.flow`, `proof_*.flow`, `lib/verify/` | `examples/verify/`, `tests/`, distinct proof parser contract | `docs/language/verification.md`, proof book (not ordinary source adoption) |

## Audit dimensions for EACH feature

Every work item that declares a feature shipped must record **exact syntax**, **actual parser/expander path**, **type and effect checks**, **lowering and runtime contract**, **target-specific behavior**, **formatter and LSP support**, **at least one positive and one negative test**, **the canonical example**, **doc link**, **stable vs experimental status** and **what remains unsupported**.

The distinction between *lexically recognized*, *parsed*, *typed*, *lowered*, *compiled*, *executed*, *numerically validated* and *portable* is mandatory. A beautiful syntax sketch is not executable evidence.

## Adoption denominator

Classify all candidate source by purpose before counting eligible migrations. Explicitly distinguish `compiler/fixtures/` (compiler oracle and negative syntax), `examples/verify/` (separate formal/proof notation), intentionally manual numerical baselines, AI-prompt adversarial files, generated files, production implementations, tutorials, and target-specific demos. A unit-bearing `f64` used as an internal normalized computation is not automatically an anti-idiom.

The feature registry should eventually generate this mapping. Until that exists, use this file for discovery only and do not duplicate its claims into more manual "status matrices".

## Machine-readable path evidence

Run `./flow tool feature_evidence` to emit `flow.feature-evidence.v1` JSON for the current Git revision. Each report records whether the worktree was clean. Each feature row preserves the map's backtick references, resolves exact paths, directory prefixes and simple `*` patterns against `git ls-files`, and lists references with no tracked match. A reference ending in `/` resolves to that prefix itself when at least one tracked file lies beneath it; it is never reported as one arbitrary member file. An empty prefix stays unresolved and counts as a gap. The report marks implementation and support status as `unverified`. A tracked path proves that an anchor exists. It does not prove that the feature works or is supported.

`./flow tool feature_evidence --roles` classifies those anchors by the column they came from: `implementation` (column 1), `semantics_or_negative` (column 2) or `teaching` (column 3), and prints `BACKEND <family> <c|mlir|wasm|gpu>` for implementation anchors that name an independent backend. A column that resolves to no tracked path prints `GAP <family> <role>`, and `--check` exits nonzero when any family has one. `--map PATH` runs either report over an alternate map, so the presence and absence of a gap are both testable. Role and backend rows inherit the same limit as the JSON report: they say which column named a path, not that the feature, target or example works.
