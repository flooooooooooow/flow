# Verification and acceptance ladder

This is the shared evidence policy for `work-packages.json` and issue/PR acceptance. It supplements `AGENTS.md`, `docs/project/agentic-loop.md`, and existing release qualification. No command or CI is proof of a property it does not test.

## Baseline before edits

Record exact `git rev-parse HEAD`, working-tree status, host/target and toolchain versions, and the relevant passing/failing test results on current `main`. Inspect active PRs, exact modified paths, and generated artifacts. When possible, demonstrate the regression's failing case on base and success on the candidate, with repeatability and negative controls. A pre-existing failure must not be labelled as caused by the PR.

## Targeted validation by surface

| Change | Required initial checks | Additional proof |
| --- | --- | --- |
| Grammar, flow blocks, DSL or unit semantics | `./flow tool compiler/scripts/parity_flow_blocks.flow`, `./flow tool compiler/scripts/parity_typecheck.flow --check` or focused `parity_field_dsl.flow` / `parity_dynamics_dsl.flow` | Wrong-unit/type/effect rejection, generated C or MLIR inspection, native execution, format roundtrip and bootstrap fixed point if compiler changed |
| Effects, handlers and lifetimes | `./flow tool compiler/scripts/parity_effects.flow`, focused `typecheck_rules.flow`, `./flow test-lang` | Handler ordering, strict errors, unknown effects, generated backend behavior |
| C/MLIR and optimizer | `./flow tool compiler/scripts/mlir_vs_c.flow --check`, focused compiler fixtures | Same source and mathematical contract on both targets, emitted IR actually verified, no illegal FP reorder/aliasing |
| Stdlib, API or DSP | `./flow test --compiler --strict --tier2` and focused executable | Golden output, scalar/oracle parity, ABI/ownership, RT alloc/block proof and performance evidence when relevant |
| Examples, scientific simulation | `./flow tool verify_examples` plus each selected `./flow run <real-file>.flow` | Analytic/reference solution, energy/conservation residual, dt/dx refinement, units and solver boundary cases; distinguish compile-only from run |
| CLI/check/LSP | `./flow tool tests/check/run.flow`, `./flow tool tests/tools/lsp/run.flow` | Same rule IDs/spans, suppressions, no unproven auto-fix, accepted transcript from actual tooling |
| Spec, tutorials, book, snippets | `./flow tool doc_examples --check-ledger`, `./flow tool doc_examples --run --check-ledger`, `./flow tool doc_coverage`, `./flow tool wiki_links` | Real syntax verified on announced backend, correct stability level and live links |
| Docs browser/WASM | `./flow tool build_wiki`, `node scripts/check_live_demos.mjs --docs-browser --wiki build/wiki` | Actual compiled WASM / Chromium checks where claimed; site accessibility and navigation, no fake native simulation |
| Release or security files | Existing release qualification and required CODEOWNER review, all exact-head required checks | No agent-granted approval, credentials exposure, policy weakening or bypass of merge-group checks |

Commands are examples from the repository's current scripts and CI. A task must first confirm the command still exists on the chosen revision. Do not pretend one command validates every touched surface. If a toolchain dependency is unavailable, report that specific gate unexecuted and do not claim portable/shipped proof.

## Scientific and numerical correctness

For a physical model, record variable definitions, actual units, initial conditions, boundary conditions, solver method, exact `dt` and discretization, event timing, reference model, maximum error and acceptable tolerance. Include an invalid-unit test, a physically invalid parameter case, a coarse/fine-step comparison and a conservation/boundedness law when applicable. Do not use a second implementation that copies all the same formulas and bugs as the only oracle.

For optimization, distinguish observational equivalence, type preservation, numerical tolerance and mere empirical resemblance. Floating point associativity, rounding, forced vectorization, IEEE corner cases, effect order, aliasing and cross-thread ordering matter. The open/merged status of issue #1694 must be checked afresh before starting related work.

For real time, `@rt_safe` is not a certified WCET guarantee. Verify transitive allocation/blocking/IO and known extern contracts, then measure deadline and resource behavior independently on the intended hardware. An `UNKNOWN` effect is not a safe absence of effects.

## Doc and feature classification gates

A feature may move from proposed to experimental only with an executable positive example and a reproducible negative check. Calling it stable requires the approved language lifecycle and compatibility criteria; code acceptance alone does not approve stability. C-only is C-only until independent MLIR, WASM or other advertised backend checks pass. Generate cards from tested source; do not manually bless invalid syntax.

## PR report template

```text
Work package: FM-XXX
Issue/claim: <link>
Base SHA: <sha>   Head SHA: <sha>
Files and purpose: <specific>
Baseline: <command and actual outcome>
New positive test: <file, command, exit and result>
New negative test: <file, expected failure and actual diagnostic>
Compiler/backend coverage: <supported/unsupported/unverified with evidence>
Numerical/RT/performance evidence: <actual, if relevant>
Full gates completed: <commands with results>
Gates not run: <specific reason, owner>
Open decisions/risks: <specific>
Remaining dependent packages: <IDs>
```

A PR is not complete until its exact final head has been checked by the required jobs and review gates. A stale earlier green check is not enough. GitHub merge queue and CODEOWNERS remain the decision-makers.

## Programme-wide exit gates

The programme is ready for maintain-mode only after: (1) all eligible feature families have independently supported status cards, including negative tests; (2) contradictions in present-tense canonical docs are resolved; (3) normal eligible new programs choose the appropriate high-level representation in held-out agent evaluations; (4) editor/checker/docs/browser show the same current syntax and limitations; (5) primary downstream packages are verified or explicitly blocked/limited; (6) none of the migrations worsen correctness, effect order, resource contract or target claims; and (7) future changes are ratcheted by a measurable, low-noise automated process.

**Do not make up a global percent-adoption target before FM-005 defines the eligible denominator.** The objective is correct representation, not advanced-syntax density.
