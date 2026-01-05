# Changelog

All notable changes to FLOW will be documented in this file.

## [0.1.0] - 2026-01-05

### Added
- Initial FLOW language implementation
- Recursive descent parser with full tokenizer
- C code generation backend for reliable execution
- MLIR generation backend (experimental)
- Struct support with field access
- OOP-style examples with method-like functions
- Composition examples with nested structs
- Classic algorithm examples (factorial, fibonacci, GCD, sorting)
- Modern Python package structure
- CLI tool with run/compile/test commands
- Comprehensive documentation

### Features
- **Language Features**:
  - Static typing with explicit annotations
  - Functions with parameters and return types
  - Control flow (if/else, while)
  - Struct definitions and literals
  - Field access (including chained access)
  - Variable declarations and assignments
  - Binary and unary operations
  - Function calls

- **Toolchain**:
  - `./flow run <file>` - Compile and execute
  - `./flow compile <file>` - Compile only
  - `./flow mlir <file>` - Generate MLIR
  - `./flow test` - Run all tests
  - `./flow examples` - List available programs

- **Backends**:
  - C backend (production-ready)
  - MLIR backend (experimental)

### Examples
- **Standard Programs**: hello_world, factorial, fibonacci, GCD, power, palindrome, prime_numbers
- **Algorithms**: bubble_sort, simple_search
- **OOP**: oop_person, oop_counter
- **Composition**: composition_car_engine, composition_team_employee
- **Data Structures**: stack implementations

### Architecture
- `src/flow/parser.py` - Tokenizer and recursive descent parser
- `src/flow/c_generator.py` - C code generation with struct support
- `src/flow/mlir_generator.py` - MLIR dialect generation
- `src/flow/transpiler.py` - Main CLI interface
- `flow` - Shell script CLI wrapper
- `pyproject.toml` - Python packaging metadata

## [0.2.0] - 2025-01-05

### Added
- **String Support & I/O**
  - String literals with double quotes: `"Hello, FLOW!"`
  - `print()` intrinsic for strings, integers, and floats
  - LLVM global string constants and printf integration

- **Array Types**
  - `array<T>` - dynamic arrays: `array<f32>` → `memref<?xf32>`
  - `array<T, N>` - sized arrays: `array<f32, 100>` → `memref<100xf32>`
  - `T[]` shorthand syntax: `f32[]` → `memref<?xf32>`
  - `[T; N]` Rust-style syntax: `[f32; 100]` → `memref<100xf32>`
  - Array indexing with `arr[i]` syntax
  - `memref.load` and `memref.store` MLIR lowering

- **Pointer Types**
  - `ptr<T>` syntax: `ptr<f32>` → `!llvm.ptr`

- **For Loops**
  - Range-based loops: `for i in 0..n { ... }`
  - Step support: `for i in 0..n step 2 { ... }`
  - Proper `scf.for` MLIR lowering with index types

- **Parallel Constructs**
  - `parallel for i in 0..n { ... }` syntax
  - `scf.parallel` MLIR lowering for auto-parallelization

- **LLDB Debugger Integration**
  - `tools/flow_debug.py` for breakpoint debugging
  - C shim wrapper for meaningful LLDB breakpoints
  - Debug symbol generation with `-g` flag

- **SIMD Verification**
  - `tools/simd_check.py` for detecting SIMD instructions in assembly
  - LLVM vectorization remarks support
  - Assembly emission for manual inspection

### Fixed
- Mixed `index`/`i32` arithmetic with automatic `arith.index_cast`
- Duplicate `_main` symbol conflict in debugger builds
- MLIR pass pipeline nesting for LLVM 21 compatibility
- String length calculation for escape sequences

### Tests
- Added `test_print_string.flow` - string and print intrinsic
- Added `test_array_types.flow` - array and pointer type syntax
- Added `test_for_parallel.flow` - for loops and parallel constructs
- Added `test_simd_saxpy.flow` - SIMD vectorization regression test
- Added `test_array_index_read.flow`, `test_array_index_write.flow`
- Added `test_nested_array_access.flow`, `test_int_memref.flow`
- All 51 tests passing

## [0.3.0] - 2025-01-05

### Added
- **DWARF Debug Info**
  - `--debug-info` flag for transpiler to emit LLVM debug metadata
  - Source file tracking in MLIR module attributes
  - Compile unit debug info for source-level debugging

- **Loop-Carried Variables**
  - Automatic detection of variables assigned inside loops
  - `scf.for` with `iter_args` for proper SSA form
  - `scf.yield` for passing values between iterations
  - Correct handling of accumulator patterns (e.g., `sum = sum + i`)

- **IntelliSense / LSP Support**
  - `src/flow/lsp_server.py` - Full LSP server implementation
  - Code completion for keywords, types, functions, and symbols
  - Hover information for functions and structs
  - Go-to-definition support
  - Document symbol outline
  - VS Code extension in `editors/vscode/flow-language/`
  - TextMate grammar for syntax highlighting

### Tests
- Added `test_loop_carried.flow` - loop-carried variable accumulator test
- All 52 tests passing

## [0.4.0] - 2025-01-05

### Added
- **Enhanced MLIR Optimization Passes**
  - `src/flow/mlir_optimizer.py` - Full optimization pipeline
  - Optimization levels: O0, O1, O2, O3
  - Available passes: canonicalize, CSE, SCCP, affine-loop-fusion
  - `--optimize`, `--opt-level`, `--no-vectorization`, `--no-loop-fusion` flags
  - `--opt-report` for detailed optimization statistics
  - `tools/flow_jit_opt.py` - JIT with optimizations enabled
  - Automatic memref casting for type compatibility
  - Fixed array literal generation to use memref instead of tensor

### Fixed
- Array literal generation from `tensor.from_elements` to memref allocation + stores
- Function call type mismatches with automatic memref casting
- MLIR optimizer pass pipeline to use only available passes

### Tests
- Added `test_optimization.flow` - optimization test with vectorizable loops
- All 53 tests passing

## [Unreleased]

### Planned
- Standard library functions
- Package manager integration
