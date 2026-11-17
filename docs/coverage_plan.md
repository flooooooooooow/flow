# Flow Coverage and Verification Plan

> **Status:** Active verification programme. This replaces the retired Python-compiler `pytest --cov=src/flow` plan. The active compiler is self-hosted in [`compiler/src/`](../compiler/src/); the public driver is [`./flow`](../flow). A numerical claim of "100% coverage" requires a separately defined, measured branch/statement denominator and must not be inferred from a green test suite.

## What must be verified

| Surface | Source of truth | Executable verification |
| --- | --- | --- |
| Lexer and core parser | [`compiler/src/lexer.flow`](../compiler/src/lexer.flow), [`parser.flow`](../compiler/src/parser.flow) | `./flow tool compiler/scripts/parse_coverage.flow --check`, `./flow test-lang`, accepted and rejected parser fixtures |
| Type checking, generics and dimensional arithmetic | [`compiler/src/sem_check.flow`](../compiler/src/sem_check.flow), [`sem_types.flow`](../compiler/src/sem_types.flow) | `./flow tool compiler/scripts/parity_typecheck.flow --check`, targeted negative tests, `./flow test-lang` |
| Continuous state, events and connections | [`compiler/src/flow_blocks.flow`](../compiler/src/flow_blocks.flow) | `./flow tool compiler/scripts/parity_flow_blocks.flow`, compiled evolution examples and analytic/numerical reference checks |
| Dynamics, fields and physics | [`dynamics_dsl.flow`](../compiler/src/dynamics_dsl.flow), [`field_dsl.flow`](../compiler/src/field_dsl.flow), [`physics_dsl.flow`](../compiler/src/physics_dsl.flow) | `parity_dynamics_dsl.flow` and `parity_field_dsl.flow` in `compiler/scripts/`, followed by compiled domain-specific examples |
| C code generation, memory and optimizations | [`compiler/src/cgen.flow`](../compiler/src/cgen.flow), native runtime, optimization modules | `./flow tool tests/cgen/run.flow`, `./flow test-lang`, generated-C inspection and negative numeric/alias/effect cases |
| MLIR and target parity | [`compiler/src/mlirgen.flow`](../compiler/src/mlirgen.flow), [`wgsl_codegen.flow`](../compiler/src/wgsl_codegen.flow) and other target modules | `./flow tool compiler/scripts/mlir_vs_c.flow --check` for C/MLIR parity; GPU shader goldens for WGSL; record unsupported targets explicitly |
| Tooling and public CLI | [`tools/flow_cli/`](../tools/flow_cli/), [`scripts/tools/`](../scripts/tools/) | `./flow test-scripts` and focused CLI, LSP, formatter and command goldens |
| Docs, examples and browser | [`docs/`](./), [`examples/`](../examples/), website builder | `./flow tool doc_coverage`, documentation-example/route checks, real Chromium live demo CI |

The checked-in [`docs/coverage.json`](coverage.json) and `./flow tool doc_coverage --inventory` describe **documented feature names**, not proof of executable semantic correctness or backend support. [`docs/grammar.ebnf`](grammar.ebnf) is an illustrative language map rather than the authoritative parser.

## Evidence requirements

Every new public feature, migration or bug fix should have a source-level reproducer, at least one accepted case and an invalid case, and the smallest affected compiler/test gate. Check the before-change failure and after-change success when reporting a regression fix. For dimensional simulation and numerical solvers, add independent analytic or oracle comparisons, convergence/stability bounds and evaluation-order constraints. For real-time code, distinguish static may-effect checks from observed deadlines. For optimizations, record floating-point ordering and target-specific differences.

Record the exact source revision, compiler/toolchain, command, exit status, assertion results and tests deliberately **not** run. Separate lexical recognition, parsing, semantic checking, lowering, native execution, numerical accuracy and cross-backend portability; passing an earlier stage does not establish a later one.

## CI ratchet

Build on the repository's existing protected checks. Start from a green baseline and add narrowly targeted regression tests with explicit paths, stable golden records and defined tolerances. Grow measured statement/branch coverage only after reliable Flow-native instrumentation exists; never introduce a mandatory `pytest` or Python-host compiler dependency to claim a coverage percentage. Keep generated bootstrap files, goldens and documentation indexes synchronized through their canonical verification commands.

See [self-hosting](project/self-hosting.md), [release qualification](project/release-qualification.md), [language testing](project/tests-in-flow.md) and the [agentic verification contract](project/agentic-loop.md) for the operating procedures.
