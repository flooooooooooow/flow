# Tests in Flow

The Python test suite under tests/unit/ and tests/integration/ holds about
880 tests. Many of them transpile a Flow snippet, compile it with clang, run
the binary, and assert on the exit code. Tests of that shape do not need
Python. They can be plain .flow programs whose main() returns 0 on success
and a nonzero check number on failure, executed by the shell harness.

This document classifies every Python test file and records the pilot
migration.

## Classes

- (a) BEHAVIORAL. Transpile, compile, run, assert exit code or stdout.
  These can become pure .flow test programs under tests/lang/.
- (b) OUTPUT-SHAPE. Assert on generated C or MLIR text. These stay
  host-side until goldens move into the self-hosted compiler.
- (c) COMPILER-INTERNAL. Unit tests of Python classes (parser AST,
  type checker diagnostics, LSP, proof tooling, package manager). These
  stay until flowc self-hosting replaces the Python compiler.

Mixed files are classified by the part that decides where they live next.
A file marked (a) keeps its host-side asserts until a later batch retires
them.

## Pilot

The pilot converts the clearest exit-code tests into seven .flow programs
under tests/lang/. Each file header names the Python tests it supersedes.
No Python tests were deleted. The harness runs them two ways:

- `./flow test --strict --tier2` sweeps all git-tracked tests/**/*.flow,
  so tests/lang/ is strict-transpiled and clang-checked automatically.
- `./flow test-lang` transpiles each tests/lang/*.flow with --strict,
  compiles it with clang, runs it, and fails on any nonzero exit.

Strict rules for tests/lang/: no flow:lenient pragma, let mut for
reassigned variables, immutable parameters, bool conditions, and/or/! for
logic.

### Converted files

| Flow test | Mirrors |
|---|---|
| tests/lang/test_arithmetic.flow | test_backend_parity.py arith program |
| tests/lang/test_control_flow.flow | test_backend_parity.py if_else, while_sum, for_sum, nested_while, while_break_via_cond |
| tests/lang/test_functions.flow | test_backend_parity.py recursive_fact, nested_calls, short_circuit_and |
| tests/lang/test_structs.flow | test_backend_parity.py struct_fields, nested_struct; test_postfix_chaining.py array-of-structs run test; test_c_generator_abi.py test_e2e_struct_field_math |
| tests/lang/test_arrays.flow | test_backend_parity.py array_sum, array_mutate_loop |
| tests/lang/test_match.flow | test_backend_parity.py bool_match, i32_match |
| tests/lang/test_closures.flow | test_closure_capture.py seven e2e tests; test_escaping_closures.py three e2e tests |

### Findings from the pilot

- Generic functions and generic struct literals fail the strict CLI type
  check (`No matching overload`, `field 'first' expects A`). The Python
  e2e generics tests bypass the checker by calling monomorphize plus
  flow_to_c directly. A generics file joins tests/lang/ once strict
  inference lands.
- Two fn-type-annotated lambda literals in one function collide on the
  generated `_flow_env` temporary and fail clang. tests/lang/test_closures.flow
  works around this by isolating one closure in a helper function. This
  deserves a compiler fix and a board card.

## Inventory: tests/unit/ (76 test files)

| File | Class | Reason |
|---|---|---|
| test_backend_parity.py | a | 15 parametrized programs run to exit code; MLIR JIT parity stays host-side |
| test_basic.py | c | pytest infrastructure smoke |
| test_c_generator_abi.py | b | substring goldens on generated C; two e2e runs mixed in |
| test_claim_address.py | c | unit tests of flow.claim_address |
| test_claim_path.py | c | unit tests of flow.claim_path |
| test_closure_capture.py | a | seven e2e run tests plus generated-C asserts |
| test_compiler_pipeline.py | a | pipeline smoke ending in compile-and-run |
| test_concurrency_codegen.py | b | asserts on generated C for concurrency intrinsics |
| test_connect_composition.py | c | parse, lowering, and typecheck of connect blocks on the Python AST |
| test_constraints.py | c | TypeChecker diagnostics |
| test_coverage_effects.py | c | effect typechecking diagnostics |
| test_coverage_flow_blocks.py | c | flow-block validation diagnostics; one run-based check migratable later |
| test_coverage_hybrid_events.py | c | hybrid-event validation diagnostics; one run-based check migratable later |
| test_coverage_known_bugs.py | c | typechecker and codegen regression pins |
| test_coverage_match.py | c | match coverage diagnostics |
| test_coverage_module_resolver.py | c | module resolver internals |
| test_coverage_units.py | c | units checker diagnostics |
| test_debug_info.py | b | #line directive shape in generated C |
| test_dual_ops.py | b | operator rewrite asserted on generated text |
| test_dynamics_dsl.py | c | dynamics DSL parse and lowering internals |
| test_effect_rows.py | c | effect-row typechecking diagnostics |
| test_escaping_closures.py | a | three e2e run tests plus parse and typecheck checks |
| test_evolves_syntax.py | c | AST and validation of evolves; one reference-Euler run check |
| test_field_dsl.py | c | field DSL internals |
| test_fuzz_crash_pins.py | c | parser crash regression pins |
| test_geometry_diagram.py | c | proof diagram tooling |
| test_geometry_proof.py | c | proof tooling |
| test_geometry_script.py | c | proof tooling |
| test_hybrid_events.py | c | parse, validation, and C-structure checks; e2e bouncing-ball runs migratable later |
| test_know.py | c | flow know lookup tool |
| test_lsp_hover.py | c | LSP internals |
| test_lsp_intel.py | c | LSP internals |
| test_match_exhaustiveness.py | c | exhaustiveness diagnostics |
| test_math_prose.py | c | math prose rendering internals |
| test_mlir_chained_ast.py | b | MLIR text goldens |
| test_mlir_effects.py | b | MLIR text goldens |
| test_mlir_generator.py | b | MLIR text goldens |
| test_mlir_match.py | b | MLIR text goldens |
| test_mlir_optimizer_passes.py | b | MLIR pass output text |
| test_mlir_postfix_chaining.py | b | MLIR text goldens |
| test_mlir_struct_parity.py | b | MLIR text goldens |
| test_mlir_vectorize.py | b | MLIR text goldens |
| test_mlir_while_cf.py | b | MLIR text goldens |
| test_module_resolver.py | c | module resolver internals |
| test_monomorphize.py | b | mangled-name asserts on generated C; its one e2e blocked on strict generics |
| test_package_manager.py | c | package manager internals |
| test_parser.py | c | parser AST internals |
| test_parser_and_or.py | c | parser AST internals |
| test_parser_array_size.py | c | parser AST internals |
| test_parser_nesting_depth.py | c | parser limits |
| test_parser_theorem.py | c | parser AST internals |
| test_pipeline_choose.py | c | choose-stage lowering internals |
| test_pipeline_placeholder.py | c | placeholder lowering internals |
| test_pointer_string_casts.py | b | generated-C text |
| test_postfix_chaining.py | a | two runnable programs migrated; AST and C-text asserts stay |
| test_proof_bundle.py | c | proof tooling |
| test_proof_document.py | c | proof tooling |
| test_proof_kernel.py | c | proof kernel internals |
| test_proof_substitution.py | c | proof kernel internals |
| test_registry.py | c | registry internals |
| test_repo_stats.py | c | repo stats tooling |
| test_rt_safety.py | c | rt_safe no-alloc diagnostics |
| test_sema_lenient_escape.py | c | lenient-mode diagnostics |
| test_shader_dsl.py | b | Metal source generated from the shader DSL |
| test_sort_expr.py | b | sort lowering asserted on generated C |
| test_strict_effects.py | b | abort-helper shape in generated C; one env-gated runtime abort check |
| test_strict_lambda_types.py | c | strict-mode lambda diagnostics |
| test_string_concat_calls.py | b | strcat lowering in generated C |
| test_tensor_ops.py | b | tensor helper rewrites in generated text |
| test_time_blocks.py | c | duration and every-block parse and validation; C-structure checks |
| test_torture_nesting.py | a | stress programs run to exit 0; parser depth checks stay |
| test_type_checker.py | c | TypeChecker diagnostics |
| test_units.py | c | units checker internals |
| test_working_mlir.py | b | MLIR text goldens |
| test_working_parser.py | c | parser AST internals |
| test_zero_cost_effects.py | b | direct-call substitution in generated C |

Support modules (not tests): \_\_init\_\_.py, compiler_helpers.py.

## Inventory: tests/integration/ (8 test files)

| File | Class | Reason |
|---|---|---|
| test_compilation_pipeline.py | c | drives the Python Transpiler API and asserts success flags |
| test_gpu_codegen.py | b | checks artifacts emitted by flow gpu |
| test_lsp_server.py | c | LSP server internals |
| test_metal.py | c | script-style Metal runtime availability probe |
| test_mlir_spirv.py | b | MLIR to SPIR-V output text |
| test_pipeline_examples.py | c | CLI transpile smoke over example programs; the tier sweeps cover this shape |
| test_real_end_to_end.py | a | compiles and runs example programs and the flow CLI |
| test_working.py | c | transpiler CLI smoke |

## Counts

| Class | unit | integration | total |
|---|---|---|---|
| (a) behavioral | 6 | 1 | 7 |
| (b) output-shape | 22 | 2 | 24 |
| (c) compiler-internal | 48 | 5 | 53 |
| total | 76 | 8 | 84 |

## Next batches

1. Migrate the remaining run-based checks inside mixed (a) files
   (test_torture_nesting.py stress runs, test_coverage_flow_blocks.py and
   test_hybrid_events.py e2e checks) once their constructs are strict-clean.
2. Add tests/lang/test_generics.flow when strict generic inference lands.
3. Retire the Python e2e twins after a few green CI cycles of test-lang.
