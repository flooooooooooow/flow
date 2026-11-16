# Flow semantic modernization and idiom adoption programme

> **Status:** proposed work programme, not approval of new language semantics.
> **Inventory baseline:** main at 7687fc936365e17bc6286415585c55fcc6ea64c3 (2026-11-16).
> **Operating contract:** AGENTS.md, docs/project/agentic-loop.md and docs/project/repository-structure.md. Existing PRs and issues take precedence over this static plan.

## Outcome

An engineer or AI agent confronting a real task should naturally choose the *highest-level correct and supported Flow representation*: units for physical quantities, flow/evolves for continuous state, every/becomes for sampled transitions, when for hybrid events, typed effects/capabilities for replaceable environmental policy, connect for valid subsystem topology, the appropriate field/dsys/circuit representation for the underlying mathematics, pipelines/forks/choose for suitable dataflow, and typed spans plus explicit real-time constraints for resource-sensitive kernels.

Do not optimize for the count of advanced features or minimum line count. Preserve mathematical meaning, evaluation order, units, effects, time semantics, lifetime, numerics, performance and target requirements. A lower-level implementation can be correct and preferable when it is a reference algorithm, specialized solver, measured hot path, FFI boundary or deliberately pedagogical example.

**Definition of done:** the compiler states what is legal; canonical executable examples demonstrate when to use each feature; tools and agents reuse the same selection knowledge; downstream flagship applications adopt these idioms where justified; all assertions have exact-revision evidence. Neither green CI nor an LLM endorsement alone qualifies semantic correctness.

## Evidence and census

The main repository's recursive Git tree contains 12,519 entries, 3,846 tracked .flow blobs and 1,455 Markdown blobs. This is an inventory, NOT an estimated migration count. Of 1,539 example .flow files, 1,054 are under examples/verify (a distinct proof/notation corpus). Compiler fixtures account for 761 of the 908 compiler .flow files. Tests include 892 .flow files; non-executable fixtures, negative tests, generated files and language-design sketches must be classified before counting them as adoption candidates.

Existing relevant work must not be duplicated: docs/idiomatic-flow.md; docs/project/pattern-adoption.md; docs/project/example-atlas.md; examples/flow_way/; Flow Idiomatics (flooooooooooow/flow-idiomatics); tools/check/main.flow and tools/lsp/diag.flow already supporting FIDIOM001/FIDIOM002; docs/project/Questions.md; compiler/src/conventions.flow; compiler/src/flow_blocks.flow; and the open Sofia symbolic-PDE PR #1703. The previous idiom-advisor issue #761 is closed and its implementation should be evaluated and extended, not re-created.

High-confidence findings from the source audit that need executable follow-up: the flow-block expander accepts dimensioned members but currently emits f64 for derivatives of unit members; the north-star document describes incomplete dimensional checking of evolves RHS; docs/grammar.ebnf, docs/language/grammar.md, docs/coverage_plan.md and parts of feature maturity/Flow Idiomatics material refer to retired Python-host compiler architecture; some north-star statuses lag the shipped connect/represent/RK4 examples. A future PR must first reproduce each claim on exact current main before changing compiler semantics or public documentation.

## Workstream A: machine-checkable feature truth

**Ownership:** docs/LANGUAGE_SPEC.md + compiler conformance fixtures + a proposed small machine-readable feature registry under docs/generated or a versioned source owned by compiler/tooling. Choose one authority path in a narrow architecture decision; do not create competing hand-edited matrices.

Each feature entry needs a stable ID, category, syntax and exact minimum supported revision, status (stable/experimental/limited/proposed/retired), host/backend/target matrix, parser and formatter coverage, type/effect/lifetime semantics, generated-runtime contract, reference fixture, negative fixture, sample executable, documentation anchor, known limitations, authorized lowering route, and migration guidance. Derive rendered coverage and agent-facing cards from this one registry where feasible.

Audit every feature claim against an implemented parser/typecheck/lowering, real compile/run evidence and explicit negative cases. Separate Flow source accepted by flowc from documentation-only sketches, third-party proof syntax, experimental libraries and an open PR. Do not describe a feature as portable unless the same source passes the required independent backend lanes.

**Initial categories:** core algebraic values, higher-order closures and matching; pipelines/forks/choose; units/quantities/complex/RF rate types; flow/evolves, solver, sampled transitions, events, invariants and guarantee; connect and nested flow; represent/sense/dsys/analyze/control; PDE/field and physics; typed math/equation notation; autodiff/Dual/Tensor; effects/capabilities/handlers, async/concurrency; memory/lifetimes/spans/RT; sorting/searching/implementation-selection constraints; graphics/shaders/GPU; verification/recognition and compiler explainability.

**Deliverable:** verified feature-by-surface matrix, unresolved decisions recorded in docs/project/Questions.md, inconsistency list with file/line, and generated linkable feature cards. No semantics change in this workstream.

## Workstream B: semantic and compiler integrations

**Core source locations:** compiler/src/lexer.flow, token.flow, parser.flow, ast.flow, sem_check.flow, sem_types.flow, sem_model.flow, expr_type.flow, flow_blocks.flow, effects.flow, dynamics_dsl.flow, field_dsl.flow, physics_dsl.flow, cgen.flow, mlirgen.flow, wasm_gen.flow, fmt.flow, rt_summary.flow, and their relevant fixtures. Touch only the modules justified by each vertical slice.

| Integration | Current evidence / reason | Required decision or verification |
| --- | --- | --- |
| Units + continuous evolution | flow_blocks accepts declared dimensions as members but emits f64 derivatives for unit members | Validate dimensions of derivative expressions, typed temporal step and generated integrators end-to-end, including wrong-unit negative cases and casting policy. Decide whether derivative storage is dimensioned or erased only after checking. |
| Time and solver contracts | every catch-up, when crossings and solver method are expanded separately | Pin update ordering, simultaneous read semantics, dt dimensions, RK4 stage semantics, stiff-system limits, event time quantization, multirate behavior, invariants and restart behavior. |
| Equation-first mathematical forms | Current flow/evolves and field/dsys surfaces are real; precise requested direct mathematical-function/equation syntax needs a dedicated parser test rather than inferred marketing language | Inventory exact supported equation/function constructs, algebraic constraints, residual equations, differentiation and lowering. Keep ODE, DAE, algebraic solve and symbolic-PDE nodes distinct. |
| Effects + capabilities | Scoped handlers and effect rows exist; capabilities currently stateless and MLIR coverage is limited | Test handler scope/nesting, strict rows, unknown effects, async/cancellation semantics, interop, multithread behavior, and effect-free derivative requirements. |
| Flow composition + control | connect and represent-linear runnable paths exist but feature status docs differ | Check algebraic loop rejection, port types/rates, signal direction, scheduling, manually specified vs generated Jacobians and restricted analysis dimensions. |
| PDE + physics | Field 1D expander works; #1703 is an experimental symbolic PDE proposal; @physics support is not a full rigid-body/DAE solver | Keep reference finite differences, typed DAG, boundary conditions, units, solver strategy, GPU targets and domain ports separate until approved and verified. |
| Numerical reproducibility | Open issue #1694 documents forced-vectorization reordering of FP reductions | Specify ordering/roundoff policy before any style rule suggests reductions, pipeline fusion or parallel execution. Preserve comparisons with independent oracle and tolerances. |
| Real-time + memory + effects | @rt_safe, cross-module summaries and lifetime annotations exist | Check transitive effects, unknown externs, dynamic dispatch, allocation, blocking, deadlines, stack/scratch and lifetimes on each supported target; no guarantee based on annotation alone. |
| Functional algebra + auto-diff | Fork/choose, closures, Dual/Tensor support vary by backend | Prove source evaluated once, effect ordering, no alias changes, differentiation correctness and C/MLIR differential execution before auto-rewrite. |
| Implementation selection and verification | General plans exist but attribute constraints and real cost units are incomplete | Do not recommend proposed syntax; make choices observable with explain plans, safety budgets, numeric contracts and provenance. |

**Gate for every compiler change:** a valid and invalid grammar test, strict type/effect/lifetime test, lowering golden or IR inspection, native C compile-and-run with assertions, MLIR parity or documented unsupported diagnostic, WASM where applicable, formatter roundtrip, LSP/docs support, bootstrap fixed-point and relevant regression coverage. Design approval is required for new syntax/semantics, public APIs, ownership, effects, and security policies.

## Workstream C: stdlib and application API contracts

**Primary owners:** lib/stdlib/units_si.flow, math.flow, rf.flow, dynamics.flow and lib/stdlib/dynamics/, circuit.flow, spice.flow, dsp.flow, audio.flow and lib/stdlib/audio/, concurrent.flow, async.flow, autodiff.flow, autodiff_reverse.flow, tensor.flow, ml_nn.flow, fixed_point.flow, time.flow, hardware.flow, rtos.flow, gfx.flow, gpu_*.flow, native/ and science/ as relevant.

Audit public API signatures for raw f32/f64 where a domain unit or rate is essential, pointer/count pairs where an accurate span is possible, hidden allocation/blocking in real-time call paths, global environmental switches that belong at an effect boundary, manually duplicated integration loops, untyped port or time domains, and custom numerical kernels that should use an existing tested facility.

Do not mechanically replace every scalar: normalized values, algorithmic internals and FFI interfaces may legitimately use raw floating point. Preserve data layout, ABI and performance. Distinguish domain model and reference implementation from deployed numerical kernel. Version or provide compatibility wrappers when changing public APIs.

**Output:** function-level audit inventory with existing signature, proposed signature, reason, risks, compatibility strategy and tests. One package or domain per implementation PR.

## Workstream D: executable examples and educational progression

**Surfaces:** examples/flow_way/, examples/basics/, evolution/, dynamics/, physics/, circuits/, neuro/, morphogenesis/, audio/, dsp/, rf/, ml/, numerical/, science/, concurrency/, effects/, systems/, gpu/, interop/, and apps/. Exclude examples/verify, parser fixtures, adversarial negatives, educational hand-integrators and intentionally target-specific examples from naïve automatic rewrite targets; tag their purposes explicitly.

Inventory each candidate by task, mathematical class, idioms presently used, preferred verified form, backend, expected output/energy or conservation oracle, numerical tolerance, performance and acceptance command. Create reproducible before/after evidence. Prioritize canonical pages and example entrypoints over obscure files.

Initial vertical proofs should be: a dimensioned braking/vehicle plant; an equation-first coupled suspension with typed boundary; a sampled thermostat with resets/invariants; an effect-swappable telemetry shell around pure control dynamics; a circuit DAE or MNA counterexample where NOT using evolves is correct; a 1D field/PDE example with convergence check; and a real-time audio block proving allocation-free transitive behavior.

Keep low-level integrator, explicit-loop and memory implementations when they teach implementation or provide independent validation. Tag them rather than bury or remove them. Promote only passing examples into examples/README.md, docs/demos/, and site/wasm/ manifests.

## Workstream E: authoritative documentation and site

**Specification and status:** docs/LANGUAGE_SPEC.md, docs/grammar.ebnf, docs/language/grammar.md, docs/language/syntax.md, docs/language/types.md, docs/language/functions.md, docs/language/overview.md, docs/language/dynamics-dsl.md, docs/language/physics-dsl.md, docs/language/rt-summaries.md, docs/language/multi-implementation.md, docs/vision/north-star.md, docs/vision.md, ROADMAP.md, VISION.md, STABILITY.md and docs/project/maturity.md. Eliminate contradictory current-status statements and mark historical designs as such.

**Teaching:** docs/idiomatic-flow.md should be the concise selection guide and link to Flow Idiomatics as the extended showcase owner. Update docs/start-here.md, docs/getting-started.md, docs/tutorials/, docs/book/, docs/effects-showcase.md, docs/library/, docs/demos/ and examples/README.md in dependency order. Every new feature needs one positive and one negative compiler-checked example, an anti-example with explanation, limits, and the correct invocation.

**AI and distribution:** docs/AI_FLOW_HANDBOOK.md, AGENTS.md, CONTRIBUTING.md, docs/project/agentic-loop.md, .cursorrules, site/, docs/playground/, site/wasm/, navigation in docs/nav.json and mkdocs.yml, tools/lsp/catalog.flow. The compiler, docs, generated site, browser preview and agent materials must not teach different languages. Do not promote an unsupported browser interpreter result as native compiler execution.

**Stale architecture cleanup:** audit docs/coverage_plan.md, docs/language/grammar.md, docs/project/maturity.md, docs/AI_FLOW_HANDBOOK.md and the Flow Idiomatics backend/host references for retired Python-host source paths, stale version statements, unsupported syntax or obsolete release claims. History belongs in archives, not present-tense references.

## Workstream F: editor, diagnostics, automation and agent guidance

**Existing implementation:** tools/check/main.flow supports --idioms with FIDIOM001/FIDIOM002. tools/lsp/diag.flow implements parallel idiom detection. Tests live in tests/check/ and tests/tools/lsp/. Extend/reconcile this rather than start a second linter.

Separate *provably equivalent* suggestions from advisory architecture selection. Share stable rule IDs, source spans, evidence, severity, suppression mechanics and supported-version metadata across CLI/LSP/PR reporting. Auto-fixes must recompile and check semantic parity, never suggest nonexistent syntax, and honor formatter, effects, lifetime and backend constraints. For high-level recommendations (use flow/evolves, a unit, or effect boundary), emit advisory explanations and examples rather than automated rewrites until proofs exist.

**Editor and browser:** update tools/lsp/catalog.flow, tools/lsp/diag.flow, compiler/src/lsp_*.flow, site/flow-lang.js, site/flow-compile.js, docs/playground/index.html, and downstream tree-sitter-flow and flow-tmLanguage grammars. Include syntax highlight, completion, hover, diagnostics, snippets, format roundtrip, working browser demos and accessibility tests.

**AI agents:** update Flow-specific skills in flooooooooooow/flow-skills (especially flow-basics, flow-dynamics, flow-effects, flow-audio, flow-autodiff, flow-compiler-dev and references/syntax-card.md). Add a selection protocol: classify mathematical/architectural problem; check exact installed feature and backend; choose canonical working example; prove negative cases; implement smallest correct form; explain deliberate fallbacks. Add prompt-based evaluation tasks to detect both *missing an idiom* and *cargo-culted overuse*. Integrate recommendations into existing agentic-loop governance; never let an advisory style detector authorize new syntax, ignore CODEOWNERS or waive independent CI.

## Workstream G: cross-repository downstream migrations

| Repository | Main adoption and compatibility audit |
| --- | --- |
| flooooooooooow/flow-idiomatics | Preserve opinionated corpus and STYLE.md as public design examples; update obsolete host and feature-state claims; extend FEATURE_MATRIX.md, executable maximal collisions, BACKEND_PARITY.md and portable-programs.txt only with verified compiler coverage. |
| flooooooooooow/herbie | Equation-first car and quarter-car models; unit-safe physical ports and tolerance/covariance APIs; sampled ECU, circuit/DAE distinction, independent solver comparison and simulation validation. |
| flooooooooooow/flow-audio | Sample-rate and frame-rate semantics, buffer/span ownership, realtime callback restrictions, effectful host boundary, DSP pipeline and CMajor parity. |
| flooooooooooow/flow-dsp | Stateful DSP and numerical characteristics, deterministic sample ordering, parameter/unit types, real-time ABI and end-to-end equivalence. |
| flooooooooooow/flow-skills | AI authoring preferences and version-qualified examples, not a competing specification. |
| flooooooooooow/tree-sitter-flow and flow-tmLanguage | Grammar, highlighting and scope updates for current stable/experimental syntax. |
| flooooooooooow/flow-compiler | Decide explicitly whether this repository is a maintained standalone compiler distribution or historical mirror; do not create two independent semantic owners. |
| flooooooooooow/flow-kernel and other consumers | Check hardware/runtime boundaries and language-version pinning; migrate only relevant domains. |
| Other downstream applications | Discover by dependency manifests, import paths and pinned compiler versions; do not assert a full population without discovery. |

For each consumer, record compiler SHA, baseline tests, actual constructs in use, blockers, API breakage risk, adoption proposals, compatibility and CI status. Stage migrations behind published, testable compiler contracts. No mass cross-repo branch changes during overlapping PRs.

## Workstream H: verification, scorecards and release ratchet

**Existing test routes to reuse as relevant:** ./flow test-lang, ./flow test-runtime, ./flow test-scripts, ./flow tool tests/check/run.flow, ./flow tool compiler/scripts/parity_flow_blocks.flow, ./flow tool compiler/scripts/parity_typecheck.flow --check, ./flow tool compiler/scripts/parity_dynamics_dsl.flow, ./flow tool compiler/scripts/parity_field_dsl.flow, ./flow tool compiler/scripts/fmt_check.flow --check, ./flow tool compiler/scripts/mlir_vs_c.flow --check, ./flow tool doc_examples --check-ledger, ./flow tool doc_examples --run --check-ledger, ./flow tool doc_coverage, ./flow tool build_wiki, ./flow tool wiki_links, node scripts/check_live_demos.mjs --docs-browser --wiki build/wiki, and relevant focused source runs. Use actual required workflow names and exact SHA evidence for each PR.

Do not assume all these gates currently pass, or that passing doc-compile checks establishes runtime behavior. Record baseline before changes. Follow the self-hosting/fixed-point procedure for compiler edits; preserve generated artifacts by regeneration. Run semantic test, differential oracle, numerical convergence, memory/RT proof, and performance benchmark only where applicable.

**Scorecard definition:** percentage of documented shipped features with exact source+negative+backend evidence; documentation-status contradictions; formatter/LSP/browser parity; newly authored eligible example adoption rate with justified exceptions; stale-syntax incidents in agent outputs; idiom-advisor precision and false-positive suppressions; migration regressions; backend disparities; measured cost/performance changes; and unresolved safety issues. Track numbers by exact revision and task class rather than unsupported global success claims. Ratchet only after a measured clean baseline.

## Rollout: dependencies, PR boundaries and exit gates

| Stage | Work package | Dependency | Evidence / acceptance |
| --- | --- | --- | --- |
| P0 | Feature census, cross-surface ownership, current grammar/semantics truth and open PR overlap | None | Every public feature family classified, source paths/feature owners/test anchors recorded, known contradictions enumerated. |
| P1 | Modernize authoritative feature cards and working example exemplars; update Flow Idiomatics statuses | P0 | No unsupported showcase advertised as runnable; docs and feature register agree with exact compiler fixtures. |
| P2 | Compiler semantics vertical slices: start units/evolution and time; then effects/RT and math/pipeline parity | P0; design approval for semantics | Targeted negative tests, runtime behavior and backend/formatter matrix pass. No unsafe mechanical rewrite. |
| P3 | stdlib API and canonical domain-example migrations | P1 + relevant P2 slice | Numerical/behavioral oracle passes, compatible API or explicit versioning, independent reference retained. |
| P4 | CLI/LSP shared idiom engine, editor and web playground correctness, AI skills | P1; reliable parser metadata | Same rule IDs/semantics for tooling; zero unverified machine-applicable fixes; agent evaluations show increased correct selection. |
| P5 | Downstream packages, tutorials, book and flagship live showcases | P3/P4 where applicable | Same source passes required target gates and deployed browser tests where advertised; version pins explicit. |
| P6 | Release ratchet, deprecation/stale-doc cleanup and ongoing adoption metrics | Clean preceding lanes | Qualified release candidate, no known contradictory current-status claims, update guardrails enabled incrementally. |

Implement one semantic purpose per PR. Begin with additive non-semantic inventory/spec corrections, do not land blanket style rewrites, and do not run generated-file merges without regeneration. Avoid ongoing overlap with PR #1703 (experimental Sofia), PR #1707 (playground accessibility) and other exact-head work. Coordinate changed paths with the existing Orchestrator protocol rather than assuming exclusive file access.

## Acceptance contract for the overall programme

A release-worthy adoption state needs (1) a verified, indexed specification for every user-facing feature family; (2) source-level plus negative conformance tests for the supported combinations of units, time, dynamics, effects, memory and solver semantics; (3) exact target/backend support and honest unsupported diagnostics; (4) examples/stdlib and flagship apps using mathematically appropriate idioms or an explicit exception; (5) compiler, docs, editor, web, agents and Flow Idiomatics agreeing on feature state and spelling; (6) an evidence-backed idiom advisor with no speculative auto-fixes; and (7) a repeatable scorecard that prevents later drift.

No numeric adoption target is asserted before P0 establishes the eligible denominator. The final condition is not “all programs rewritten”: it is that new code defaults to the right representation, existing canonical code teaches it, legitimate lower-level exceptions remain clear, and all relevant semantic and execution claims can be reproduced.

## Explicit decision boundaries

The programme does not pre-approve new equation syntax, derivative unit erasure policy, static-versus-runtime guarantee semantics, generalized DAE or PDE solver ownership, algebraic effects continuation semantics, resource/timing proof models, changes to stable public APIs, or new security/agent permissions. Record options, compatibility and counterexamples in docs/project/Questions.md and obtain the required human design decision before implementing them.

## First executable task batch

Start with a read-only generated census of feature-family x compiler stage x target x documentation x editor x example x downstream consumer, with exact filenames and references; verify the outdated claims above against actual main. Then add negative tests for unit-bearing dynamics and define the desired dimensional semantics by design review. In parallel, update only unambiguous stale docs and begin the Flow Idiomatics baseline refresh. Next build a representative end-to-end dimensioned physical model, preserving a hand-integrated reference. The same model will become the first test of agent default choices and the idiom advisor's advisory rule.
