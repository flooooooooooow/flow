# Tests in Flow

The Python test suite under tests/unit/ and tests/integration/ holds about
880 tests. Many of them transpile a Flow snippet, compile it with clang, run
the binary, and assert on the exit code. Tests of that shape do not need
Python. They can be plain .flow programs whose main() returns 0 on success
and a nonzero check number on failure, executed by the shell harness.

This document classifies every Python test file and records the pilot
migration.

The Python C backend is now retired, and flowc is the only C compiler. Python
tests that drove the Python C backend are removed or rewritten against flowc.
Language tests are `tests/lang` (`./flow test-lang`), and C output goldens are
`tests/cgen` (`tests/cgen/run.sh`). The inventory below records the files as
they were classified before the retirement.

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

## Batch 2

Batch 2 swept every file in tests/unit/ and tests/integration/ for tests
that build a program and run it. Each .flow file below passes
`./flow test-lang` and also compiles and exits with the expected code under
the Stage-A compiler (compiler/build/flowc_bootstrap, bundle mode). The
Python tests it names were deleted.

| Flow test | Supersedes |
|---|---|
| tests/lang/test_basics_smokes.flow | test_misra_euler_batch.py (whole file); test_misra_phase2.py::test_checked_arith_smoke_runs |
| tests/lang/test_cast_in_string_concat.flow | test_cast_in_string_concat.py: four of six tests |
| tests/lang/test_counted_loop_rotation.flow | test_counted_loop_rotation.py::test_expected_iteration_counts |
| tests/lang/test_defer_ordering.flow (+ .expected) | test_defer_ordering.py::test_falling_off_the_end_still_runs_defers_once |
| tests/lang/test_function_attributes.flow | test_attributes.py: the @inline, @noinline, @always_inline and @target run tests |
| tests/lang/test_if_expression.flow | test_if_expression.py::test_if_expression_runs |
| tests/lang/test_max_iterations_abort.flow (+ .exitcode, .expected-stderr) | test_decorator_arguments.py::test_the_counter_stops_a_loop_that_exceeds_its_bound |
| tests/lang/test_selective_import.flow | test_bundle_symbol_closure.py::test_compile_bundle_symbol_closure |
| tests/lang/test_span_borrow_once.flow | test_span_narrowing_evaluates_once.py (whole file) |
| tests/lang/test_span_slice_f64.flow | test_flowc_span_element_type.py (whole file) |
| tests/lang/test_stdlib_math_import.flow | test_stdlib_c_declarations.py::test_the_math_example_runs_and_is_correct |
| tests/lang/test_tco_shim.flow | test_tco_shim.py::test_shim_tail_call_runs_correctly |
| tests/lang/test_variadic_externs.flow (extended header) | test_variadic_externs.py::test_runtime_varargs_reach_libc |

test_max_iterations_abort.flow compiles under Stage-A, but Stage-A drops the
bound and the binary exits 0 (#940). The bootstrap suite only checks that
each file compiles, so it stays green.

### Run tests that stay in Python

These behaviours passed under the retired Python C backend but failed under
flowc, or failed the strict checker, when this table was written. Each
Python test stayed until its issue was fixed.

| Python test | Blocker |
|---|---|
| test_array_return.py value tests | #943 array return, #944 nested arrays, #945 `[v; N]` |
| test_cast_in_string_concat.py: numeric operand tests | #946 |
| test_defer_ordering.py: three tests | #947 |
| test_range_algebra.py (integration), test_range_sum.py run tests | #949 |
| test_private_function_module_collision.py | #950 |
| test_tco_shim.py::test_deep_tail_recursion_runs_without_stack_overflow | #951 |
| test_pthread_binding.py lock-size test | #952 sizeof and mutex calls; #953 test-lang link on macOS |
| test_match_exhaustive_returns.py::test_every_arm_still_dispatches_to_its_own_variant | #941 |
| test_complex_types.py::test_complex_compile_and_run | #942 |
| test_c_generator_abi.py::test_e2e_generic_box_after_mono | #954 inferred generic struct literal |
| test_evolves_syntax.py and test_flow_dimensioned_state.py flow-block runs | #681 flow blocks in Stage-A |

Run tests that stay for their own reasons: the MLIR JIT parity tests
(test_backend_parity.py, test_backend_parity_extended.py), tests whose
subject is a clang warning or flag (test_array_return.py stack-address
check, test_attributes.py -O2 and nm checks, test_time_header_externs.py),
tests of a Python pass that the transpiler does not call
(test_pipeline_fusion.py fusion correctness, the rotation-equivalence tests
in test_counted_loop_rotation.py), comparisons against a Python reference
(test_time_blocks.py rk4), and tool tests. The tool tests have since left
Python: test_flow_run.py is now tests/flow_run/run.sh, and the gfx recorder,
GIF encoder and other subprocess-only files are shell tests under
tests/scripts, run by tests/scripts/run.sh.

## Inventory: tests/unit/ (165 test files)

| File | Class | Reason |
|---|---|---|
| test_arena.py | b | arena helpers asserted on generated C |
| test_arith_safety.py | b | checked-arithmetic lowering in generated C |
| test_array_repeat.py | c | `[v; N]` typecheck and lowering internals |
| test_attributes.py | c | attribute parse and lowering; run checks live in tests/lang |
| test_backend_parity.py | b | C runs moved to tests/lang; MLIR JIT parity stays host-side |
| test_backend_parity_extended.py | b | C versus MLIR differential parity |
| test_basic.py | c | pytest infrastructure smoke |
| test_benchmarks.py | c | benchmark harness tooling; now tests/bench_harness/run.sh |
| test_bpf_target.py | c | eBPF target checks |
| tests/scripts/browser_interpreter_gallery.sh | c | browser interpreter tooling; now a shell test |
| test_bundle_symbol_closure.py | c | bundle symbol closure internals |
| test_c_generator_abi.py | a | substring goldens on generated C; one run test blocked (#954) |
| test_c_generator_assignments.py | b | assignment lowering in generated C |
| test_c_import_glibc_forms.py | c | @cImport header reader internals |
| test_c_import_macros.py | c | @cImport macro reader internals |
| test_c_import_no_redeclare.py | b | redeclaration shape of generated C |
| test_claim_address.py | c | unit tests of flow.claim_address |
| test_claim_path.py | c | unit tests of flow.claim_path |
| test_closure_capture.py | b | run tests moved to tests/lang; generated-C asserts remain |
| test_compiler_pipeline.py | b | run test moved to tests/lang; a clang -fsyntax-only smoke remains |
| test_complex_types.py | a | typecheck and lowering; one run test blocked on Stage-A (#942) |
| test_concurrency_codegen.py | b | asserts on generated C for concurrency intrinsics |
| test_connect_composition.py | c | parse, lowering, and typecheck of connect blocks on the Python AST |
| test_const_folding.py | b | MLIR constant folding text |
| test_constraints.py | c | TypeChecker diagnostics |
| test_conventions.py | c | project convention checks |
| test_coverage_effects.py | c | effect typechecking diagnostics |
| test_coverage_flow_blocks.py | c | flow-block validation diagnostics; one run-based check migratable later |
| test_coverage_hybrid_events.py | c | hybrid-event validation diagnostics; one run-based check migratable later |
| test_coverage_known_bugs.py | c | typechecker and codegen regression pins |
| test_coverage_match.py | c | match coverage diagnostics |
| test_coverage_module_resolver.py | c | module resolver internals |
| test_coverage_units.py | c | units checker diagnostics |
| test_debug_info.py | b | #line directive shape in generated C |
| test_decorator_arguments.py | c | decorator argument parsing |
| tests/scripts/demo_gallery_docs.sh | c | docs tooling; now a shell test |
| tests/scripts/doc_anchors.sh | c | docs tooling; now a shell test |
| tests/scripts/doc_coverage.sh | c | docs tooling; now a shell test |
| test_dsp_pipeline.py | c | DSP pipeline lowering internals |
| test_dual_ops.py | b | operator rewrite asserted on generated text |
| test_dynamics_dsl.py | c | dynamics DSL parse and lowering internals |
| test_dynamics_dsl_regressions.py | c | dynamics DSL internals |
| test_ensure_flowc_staleness.py | c | build tooling |
| test_escaped_strings.py | b | string literal escaping in generated C |
| test_escaping_closures.py | c | run tests moved to tests/lang; parse and typecheck checks remain |
| test_evolves_syntax.py | a | AST and validation of evolves; reference-Euler run blocked on flow blocks in Stage-A (#681) |
| test_export_abi.py | b | --export ABI shape in generated C |
| test_field_dsl.py | c | field DSL through the flowc expander; parity lives in `compiler/scripts/parity_field_dsl.sh` |
| test_flow_dimensioned_state.py | a | parse and validation; one integration run blocked on flow blocks in Stage-A (#681) |
| test_frontend_cache.py | c | frontend cache internals |
| test_fuzz_crash_pins.py | c | parser crash regression pins |
| test_general_plans.py | c | plan selection internals |
| test_geometry_diagram.py | c | proof diagram tooling |
| test_geometry_proof.py | c | proof tooling |
| test_geometry_script.py | c | proof tooling |
| tests/scripts/gif_flow_encoder.sh | b | GIF bytes decoded by scripts/tools/gif_check, a Flow GIF reader; now a shell test |
| test_gpu_runtime.py | c | GPU runtime probes |
| test_grow_helpers.py | b | growth helpers in generated C |
| test_hybrid_events.py | c | parse, validation, and C-structure checks; e2e bouncing-ball runs migratable later |
| test_idioms.py | c | idiom checker |
| test_if_expression.py | c | if-expression parse and typecheck |
| test_imported_main.py | b | entry-point isolation in generated C |
| test_inline_exp_nested.py | b | MLIR inline exp text |
| test_know.py | c | flow know lookup tool |
| test_lifetime_domains.py | c | lifetime-domain diagnostics |
| test_match_exhaustive_returns.py | a | one run test blocked on Stage-A (#941); -Werror=return-type check is (b) |
| test_match_exhaustiveness.py | c | exhaustiveness diagnostics |
| test_math_prose.py | c | math prose rendering internals |
| test_metal_codegen.py | b | Metal source text |
| test_misra_phase2.py | c | MISRA tooling |
| test_mlir_array_constructor.py | b | MLIR text goldens |
| test_mlir_canonicalize.py | b | MLIR text goldens |
| test_mlir_canonicalize_aosoa.py | b | MLIR text goldens |
| test_mlir_chained_ast.py | b | MLIR text goldens |
| test_mlir_closures.py | b | MLIR text goldens |
| test_mlir_effects.py | b | MLIR text goldens |
| test_mlir_generator.py | b | MLIR text goldens |
| test_mlir_match.py | b | MLIR text goldens |
| test_mlir_match_bindings.py | b | MLIR text goldens |
| test_mlir_optimizer_passes.py | b | MLIR pass output text |
| test_mlir_or_patterns.py | b | MLIR text goldens |
| test_mlir_postfix_chaining.py | b | MLIR text goldens |
| test_mlir_spans.py | b | MLIR text goldens |
| test_mlir_spirv_metal.py | b | SPIR-V and Metal output |
| test_mlir_struct_parity.py | b | MLIR text goldens |
| test_mlir_vectorize.py | b | MLIR text goldens |
| test_mlir_while_cf.py | b | MLIR text goldens |
| test_module_reexport.py | c | module resolver internals |
| test_module_resolver.py | c | module resolver internals |
| test_module_statics.py | c | module-static diagnostics and lowering |
| test_monomorphize.py | b | mangled-name asserts on generated C; its one e2e blocked on strict generics |
| test_ordering_hints.py | c | ordering-provenance pass internals |
| test_package_manager.py | c | package manager internals |
| test_parser.py | c | parser AST internals |
| test_parser_and_or.py | c | parser AST internals |
| test_parser_array_size.py | c | parser AST internals |
| test_parser_nesting_depth.py | c | parser limits |
| test_parser_semicolon_separator.py | c | parser AST internals |
| test_parser_theorem.py | c | parser AST internals |
| test_physics_dsl.py | c | physics DSL internals |
| test_pipeline_choose.py | c | choose-stage lowering internals |
| test_pipeline_fusion.py | c | pipeline fusion internals |
| test_pipeline_placeholder.py | c | placeholder lowering internals |
| test_plan_selector.py | c | plan selector internals |
| test_pointer_string_casts.py | b | generated-C text |
| test_postfix_chaining.py | c | runnable programs moved to tests/lang; AST and C-text asserts stay |
| test_project_test_runner.py | c | removed with the Python runner; its cases are in compiler/scripts/parity_project_test.sh |
| test_proof_bundle.py | c | proof tooling |
| test_proof_document.py | c | proof tooling |
| test_proof_kernel.py | c | proof kernel internals |
| test_proof_substitution.py | c | proof kernel internals |
| test_pthread_binding.py | a | lock-size run blocked (#952, #953); declarations are (b) |
| test_ptr_address.py | b | address-of lowering in generated C |
| test_python_export_overrides.py | c | Python export tooling |
| test_quantity_literals.py | c | quantity literal desugaring |
| test_range_algebra.py | c | range algebra folding internals |
| test_recognition_semantics.py | c | denotational semantics internals |
| test_registry.py | c | registry internals |
| tests/scripts/repo_stats.sh | c | repo stats tooling; now a shell test |
| test_rf_types.py | c | RF type checking |
| test_rt_safety.py | c | rt_safe no-alloc diagnostics |
| test_safety_profile_enforcement.py | c | safety profile diagnostics |
| test_security_invariants.py | c | release security checks |
| test_sema_lenient_escape.py | c | lenient-mode diagnostics |
| test_shader_codegen_wgsl.py | b | WGSL source text |
| test_shader_dsl.py | b | Metal source generated from the shader DSL |
| test_shape_specialization.py | c | shape specialization internals |
| tests/scripts/size_regression.sh | c | binary size check; now a shell test |
| test_sort_expr.py | b | sort lowering asserted on generated C |
| test_span_data_field.py | c | span typechecking |
| test_spans.py | c | span typechecking and lowering |
| test_strict_effects.py | b | #line directives in generated C; the effect checks moved to compiler/scripts/parity_effects.sh |
| test_strict_gaps.py | c | strict-mode typechecking regressions |
| test_strict_lambda_types.py | c | strict-mode lambda diagnostics |
| test_string_concat.py | b | string concat lowering in generated C |
| test_struct_literal_return.py | b | struct literal return in generated C |
| test_tco_shim.py | a | deep-recursion run blocked on Stage-A (#951); shim shape is (b) |
| test_tensor_ops.py | b | tensor helper rewrites in generated text |
| test_theorem_parameters.py | c | theorem parser internals |
| test_time_blocks.py | c | duration and every-block parse and validation; C-structure checks |
| test_torture_nesting.py | c | stress runs moved to tests/lang/test_torture.flow; parser depth checks stay |
| test_transitive_const.py | c | const visibility internals |
| test_type_checker.py | c | TypeChecker diagnostics |
| test_units.py | c | units checker internals |
| test_unknown_type_diagnostic.py | c | typechecker diagnostics |
| test_variadic_externs.py | b | variadic extern emission in C and MLIR |
| test_vectorization_audit.py | b | vectorization report on generated code |
| test_version.py | c | version string |
| test_wasm_compiler.py | c | WASM toolchain probes |
| test_wcet_analysis.py | c | WCET analysis internals; deleted with wcet_analysis.py, see tests/tools/analyze/run.sh |
| tests/scripts/wiki_nav.sh | c | docs tooling; now a shell test |
| test_working_mlir.py | b | MLIR text goldens |
| test_working_parser.py | c | parser AST internals |
| test_zero_cost_effects.py | b | direct-call substitution in generated C |

Support modules (not tests): the package \_\_init\_\_.py files and compiler_helpers.py, all since deleted.

## Inventory: tests/integration/ (21 test files)

| File | Class | Reason |
|---|---|---|
| test_array_return.py | a | value tests blocked on Stage-A (#943, #944, #945); one clang-warning check is (b) |
| test_cast_in_string_concat.py | a | two numeric-operand tests blocked on Stage-A (#946) |
| test_compilation_pipeline.py | c | drives the Python Transpiler API and asserts success flags |
| test_counted_loop_rotation.py | c | rotation equivalence calls the transform directly; MLIR fixture check |
| test_defer_ordering.py | a | three tests blocked on Stage-A (#947) |
| tests/scripts/gfx_recorder.sh | c | `flow record` tool reads back a frame; now a shell test |
| test_gpu_codegen.py | b | checks artifacts emitted by flow gpu |
| test_metal.py | c | script-style Metal runtime availability probe |
| tests/scripts/mlir_math_override.sh | b | MLIR math lowering; now a shell test |
| test_mlir_spirv.py | b | MLIR to SPIR-V output text |
| test_pipeline_examples.py | c | CLI transpile smoke over example programs; the tier sweeps cover this shape |
| test_private_function_module_collision.py | a | blocked on Stage-A (#950) |
| test_range_algebra.py | a | run tests blocked on Stage-A (#949); one C-text check |
| test_range_sum.py | a | run tests blocked on Stage-A (#949); parse checks are (c) |
| test_real_end_to_end.py | c | transpile and CLI smoke over examples; no program run asserts |
| tests/scripts/run_build_isolation.sh | c | concurrent `flow run` isolation; now a shell test |
| test_stdlib_c_declarations.py | b | libm naming and include-once checks on generated C |
| test_time_header_externs.py | b | -Werror compile and C-text check |
| tests/scripts/wasm_backends.sh | c | WASM page builder; now a shell test |
| test_working.py | c | transpiler CLI smoke |

## Counts

| Class | unit | integration | total |
|---|---|---|---|
| (a) behavioral | 7 | 6 | 13 |
| (b) output-shape | 50 | 5 | 55 |
| (c) compiler-internal | 109 | 9 | 118 |
| total | 166 | 20 | 186 |

## Next batches

1. As each Stage-A issue listed under Batch 2 closes, port its Python run
   test into tests/lang/ and delete the Python twin.
2. Rows marked (a) are files that still hold a blocked run test.
