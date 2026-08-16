# Flow Test Coverage Plan (Target: 100%)

To achieve 100% test coverage across the Flow compiler (`src/flow/*.py`), the following steps are required:

1. **Parser Tests (`src/flow/parser.py`)**:
   - Add unit tests for edge cases in error recovery.
   - Add targeted tests for specific syntax branches (e.g., DSL parsing, generic instantiations).
2. **Type Checker Tests (`src/flow/type_checker.py`)**:
   - Write tests for deeply nested generic type resolution.
   - Cover overload resolution edge cases and numeric promotion paths.
   - Ensure all `TypeError` branches are hit with intentionally malformed source code.
3. **Backend Translators (`c_generator.py`, `mlir_gpu_codegen.py`, `wgsl_codegen.py`, `python_generator.py`)**:
   - For `c_generator.py`, test corner cases of pointer arithmetic and nested structs.
   - For `mlir_gpu_codegen.py` and `wgsl_codegen.py`, create shader and compute kernels that exercise every AST node type.
   - For `python_generator.py`, test the transpilation of all Flow constructs (especially `effect` and `capability`).
4. **Optimizers (`mlir_optimizer.py`, `fir_opts.py`, `pipeline_fusion.py`)**:
   - Create synthetic IR and AST graphs that trigger each optimization pass, verifying both the condition checks and the transformation logic.
5. **DSL Implementations (`physics_dsl.py`, `shader_dsl.py`)**:
   - Write tests specifically parsing and analyzing DSL blocks.
6. **Execution Pipeline (`run.py`, `repl.py`, `test_runner.py`)**:
   - Use `unittest.mock` to simulate CLI interactions, subprocess execution, and standard library loading.

**Continuous Integration**:
We should integrate `pytest --cov=src/flow --cov-fail-under=100` into the CI pipeline once coverage reaches 100%, and progressively increase the `fail-under` threshold until then.

