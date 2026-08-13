# Changelog

All notable changes to FLOW will be documented in this file.

## Unreleased

### Release engineering

- `scripts/sync_version.py` makes `src/flow/version.py` the single source of
  truth for the version and rewrites every mirror from it: `flow.toml`,
  `pyproject.toml`, `CITATION.cff`, the README table, the language spec
  header, the three strings in the `flow` driver, and the Homebrew formula.
  `--check` verifies without writing, `--set X.Y.Z` bumps.
- CI gains an ungated `Version consistency` job running `--check`. The
  drift-prone files sit outside every existing paths filter, so the job
  deliberately runs on every push.
- `.github/workflows/version-bump.yml` syncs the tree on a `v*` tag push (or
  manual dispatch) and opens a PR. The Homebrew formula is only touched once
  the release tarball is actually published, with a digest computed from it
  rather than guessed.

## [0.11.0] - 2026-08-13

### Zero-bridge C interop

- `@cImport("header.h") as alias` parses a C header and makes its
  declarations available to Flow without a hand-written binding layer.
  Backed by `src/flow/c_header_parser.py`, covering typedefs, structs,
  enums, function signatures, and opaque types.
- `@cInclude("header.h")` emits an include with no Flow-side binding.
- `@cEmbed("raw C")` emits C verbatim after the standard includes and
  before the Flow runtime helpers, for static inline helpers and macro
  wrappers that cannot be expressed as extern declarations. Multiple
  directives accumulate.
- `extern type Name` declares an opaque C type usable behind `ptr<Name>`.
- `cfn(A) -> R` types a plain C function pointer, so callbacks such as
  `qsort` comparators and `pthread_create` entry points take Flow
  functions directly.
- The C header parser is ported to Flow as `compiler/src/c_parser.flow`,
  and `@cImport` / `@cEmbed` / `cfn` are implemented in the self-hosted
  compiler as well as the Python host.
- Tests cover `string.h`, `time.h`, `sys/stat.h`, stdlib, Python, and
  Julia headers.

### BLAS and LAPACK

- `lib/stdlib/blas.flow` bindings over Apple Accelerate on macOS and
  OpenBLAS on Linux: `gemm`, `solve`, `matmul`, `eye`, `ones`, and
  in-place variants for allocation-free use.
- `benchmarks/blas_vs_naive.flow` and [BLAS bindings](../blas-bindings.md).

### Self-hosted compiler (`flowc`)

Roughly thirty changes closing the gap between `flowc` and the Python
host on real language surface:

- Parser: semicolons and `elif`, `not`, keyword field names, keyword
  `let` names, trailing commas in array literals, scientific notation,
  hex literals, `DOTDOT` lexing, newline-separated struct fields,
  statement attributes, type aliases, generic structs, `&`/`[T]` types,
  `export type`, unit declarations, function pointer types, effect and
  capability blocks, postfix calls, extern functions and extern block
  signatures.
- Types and codegen: `println`/`print` intrinsics, `stdbool.h` emission
  for `bool`, wider integer types, bitwise `~ & | ^`, shift operators,
  compound assignment, top-level `let`, `array<T, N>` struct fields and
  top-level lets emitted as `T name[N]`, `c64`/`c128` complex
  constructors, self-referential struct pointer fields via struct tag,
  `return void` lowered to a bare `return`, string-typed identifier
  detection for `str_concat`, stdlib import resolution and `math.h`.
- Skips Flow-defined functions that shadow C standard library names, with
  an expanded libc skip list.
- Lenient bundle typecheck and `fir_analysis`.

### RF and units (W0)

- `c64` / `c128` complex types over C99 `_Complex`, with constructors and
  `creal`/`cimag`/`cabs`/`carg`/`conj`/`cexp`/`clog`/`csqrt`/`cpow`.
- `lib/stdlib/rf.flow`: `IQ` alias, distinct `IQSample`, and `Signal<R>`
  carrying its sample rate as a phantom type parameter, so mixing rates
  is a compile-time error.
- Quantity literal syntax (`3.14 Hertz`) and `lib/stdlib/units_si.flow`.
- `examples/rf/`: DFT, IQ mixer, SDR receiver.

### DSP pipelines (W1)

- `lib/stdlib/dsp.flow` with `map`, `filter`, `reduce`, `scan`,
  `zip_with`, `scale`, `offset`, `clip`, `sum`, `dot`, chained with `|>`.
- Compile-time fusion of adjacent `map` / `scale` / `offset` stages.

### Safety profiles

- MISRA 17.2 and 17.4 enforced at type-check time; `println` routed
  through `FLOW_LOG`.
- `@safe` / `@unsafe` annotations, `analyze`, and certification docs.
- `@max_iterations` required on `while` under the safety and flight
  profiles.
- `--profile flight` bans compiler-injected heap allocation, including
  the temporary arena.

### Analysis

- WCET and stack depth analysis.
- Cost-based multi-implementation selection generalised beyond `sort`.

### MLIR

- Large unsigned integer literals exceeding signed i32 range are
  converted to two's complement representation.
- `CastExpression` wrapping a `Literal` and `UnaryOperation` negation on
  a `Literal` are handled in module static constant emission.
- String interning and static LLVM array global emission for
  pointer/string element arrays.
- Constant static initialisation; the unsigned flag is dropped on a
  no-op cast to a signed type.

### Fixes

- Nested assignment expressions lower correctly in the C generator.
- Overload resolution treats `string` and `ptr<i8>` as compatible.
- `-O2` is the default optimisation level; pointer address type check.
- `strtod` fix, `--export` ABI, wasm32 data layout, Python runner.

### Removed

- Runtime overflow-checked arithmetic codegen (`FLOW_CHECKED_*` macros,
  `flow_overflow_handler`, `flow_div_by_zero_handler`,
  `flow_shift_ub_handler`). The `overflow_check` parameter on
  `flow_to_c` and `CGenerator` is gone. Literal div-by-zero and shift UB
  are still rejected at type-check time.
- `--emit-manifest` / `--manifest-format` CLI flags and the
  `safety_manifest` module. `--profile safety` still sets strict C
  compiler flags (`-Werror -pedantic`).

  Both were introduced during the 0.10.0 cycle and removed before this
  release, so the corresponding 0.10.0 notes below no longer describe
  shipped behaviour.

## [0.10.0] - 2026-08-08

### MLIR / WASM epic #221 (complete)

- **MLIR backend on par with C** for the affected surface: `uN`/`null`/
  memref coercions, bitwise and shift ops lowered to `arith`, per-function
  symbol-table restores, module globals in loops/if/vectorizer, variadic
  externs (`...`) with `llvm.call vararg`, fixed-size arrays as `llvm.array`
  struct fields, and static string-array globals.
- **WebAssembly gallery**: 118 Flow examples compiled to `site/wasm/`.
- **wasm crossings**: CPython embedding routed to Pyodide, browser file I/O
  (MEMFS + IDBFS), host-page-sized canvas.
- SPIR-V GPU emission advanced alongside the CPU backend.

### Compiler frontend

- `flowc` self-hosting: checked-in bootstrap, whole-compiler self-compile
  three generations deep, CI-gated; string concatenation and inferred C type
  for unannotated `let`.
- `flow explain` subcommand with the float total-order resolution.
- Cost-based plan selector for `sort`/`find` (merge/quick/gap/heap
  families), adaptive ordering benchmark with measured numbers.

### Language

- Lifetime domain annotations and their four checks; frame domain wired to
  the arena; LSP hover for `@lifetime`; an audio example split across all
  four domains.
- Float total order per the spec.

### Standard library

- `render3d` — software 3D renderer with pipeline documentation and measured
  rates.
- `psychstats` and `experiment` — the analysis and presentation halves of
  experiment support; `automata` cellular-automaton framework.
- Audio safety chain, WAV render target, and DSP fixes.

### Safety profiles

- `--profile safety` enables opt-in overflow-checked signed integer
  arithmetic (`__builtin_*_overflow`), division by zero guards, and shift
  undefined behaviour rejection at compile time (literals) and runtime.
- `-Werror` enforced on all C output under the safety profile.
- UBSan, ASan, and TSan available via `FLOW_UBSAN=1`, `FLOW_ASAN=1`,
  `FLOW_TSAN=1` environment variables.
- `--emit-manifest` produces a structured compliance report mapping each
  invariant to MISRA/CERT rules with PROVEN, REJECTED, or REQUIRES EVIDENCE
  status.

### Runtime

- `flow_rt_sysinfo` reduced to syscalls and compile-time facts; race
  detection relocated to `lib/runtime/race.flow`; zombie headers deleted.

### Examples and gallery

- Morphogenesis wave-2 (19 examples, gallery GIFs); genetics suites; planet
  pipeline (cubesphere, tectonics, elevation).
- Games: physics3d, raycast_shooter, Icy Tower, The Falling Sand Game,
  billboard particles; software-3D clips recorded offline.
- Numerical: Carrier–Greengard–Rokhlin adaptive FMM.

### Branding, editor, CI

- Flow logos replace text F glyphs; VS Code uses the logo as the `.flow`
  icon.
- CI/Discord: rich embeds via a single action, worded `#announcements`,
  PR notices, docs deploy pings, and a `#projects` forum for releases.

## [0.2.0] - 2026-01-08

### Added
- **Metal GPU Integration**: Native Apple Silicon GPU support
- **GPU Runtime**: Comprehensive GPU backend system with Metal, CUDA, and OpenCL support
- **Metal Runtime API**: Complete Metal framework integration for macOS
- **GPU Memory Management**: Unified memory architecture support
- **Shader Compilation**: Metal Shading Language (MSL) code generation
- **Performance Benchmarking**: GPU vs CPU performance comparison tools
- **Documentation Wiki**: MkDocs-based HTML documentation system
- **Project Organization**: Restructured documentation and cleaned up root directory

### Features
- **Metal GPU Backend**:
  - Automatic Metal detection on Apple Silicon
  - Metal shader compilation and execution
  - GPU memory allocation and management
  - Unified memory architecture optimizations
  - Real-time GPU information and statistics

- **GPU Programming**:
  - Cross-platform GPU backend detection
  - GPU kernel generation from FLOW functions
  - Memory transfer between host and device
  - Synchronization and error handling

- **Documentation System**:
  - HTML wiki with Material theme
  - Live preview and hot reload
  - Search functionality
  - Responsive design for mobile
  - Organized navigation structure

### Examples
- **Metal GPU Examples**: Metal FFT, audio processing, image filtering
- **Performance Benchmarks**: GPU vs CPU performance comparisons
- **GPU Integration**: Real-world GPU computing examples

### Documentation
- **Graphics Programming Guide**: Complete Metal GPU documentation
- **Core Library Reference**: GPU runtime API documentation
- **Metal Examples**: Comprehensive GPU programming examples
- **Project Documentation**: Organized project structure and changelog

### Architecture
- `src/flow/metal_runtime.py` - Metal GPU backend implementation
- `src/flow/gpu_integration.py` - Cross-platform GPU integration
- `src/flow/gpu_runtime.py` - Generic GPU runtime interface
- `docs/` - Complete MkDocs documentation system
- `mkdocs.yml` - Documentation configuration

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
  - VS Code extension in `third_party/integrations/vscode/flow-language/`
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

## [0.5.0] - 2026-01-08

### 🎉 Major Release - Project Cleanup & Documentation Overhaul

### Added
- **Complete Documentation System**
  - Wiki-style documentation rivaling Rust/C++/Mojo quality
  - Comprehensive getting-started guide with installation instructions
  - Beginner/Intermediate/Advanced tutorials with progressive learning paths
  - Complete language reference with syntax, types, and features
  - Standard library documentation with API reference
  - Organized example gallery with 9 categories and detailed READMEs
  - Cross-references and navigation between all documentation sections

- **Enhanced Type System**
  - Full u8 integer type support in C generator
  - Complete integer type mapping: u8, u16, u32, u64, i8, i16, i32, i64
  - Floating point type support: f32, f64
  - Fixed stdio.h include for printf support
  - Proper C type generation for all FLOW types

- **Graphics Module Foundation**
  - Created `src/graphics.flow` with comprehensive graphics types
  - Color types: Color (u8 RGBA), RGB, RGBA with utility functions
  - Geometry types: Point, Point2D, Rectangle, Rect2D
  - Color creation functions: color_rgb(), color_rgba(), color_black(), etc.
  - Point and rectangle utilities: point(), rect2d(), clamp functions
  - Type-safe graphics operations ready for import system

- **Project Organization**
  - Moved 7 misplaced examples from tests/ to examples/
  - Removed temporary files (bench_log.txt, srir_demo.txt, debug_test.flow, etc.)
  - Organized tests into proper categories: core/, stdlib/, gpu/, experimental/, misc/
  - Created comprehensive project structure documentation
  - Professional folder organization with clear separation of concerns

- **Example Gallery Enhancement**
  - 27 working examples organized into 9 categories:
    - basic/ (3 examples): Hello World, Fibonacci, Loops
    - data-structures/ (3 examples): Stack, Composition, OOP
    - algorithms/ (3 examples): Bubble Sort, GCD, Power
    - graphics/ (3 examples): SRIR demos, PPM generation
    - performance/ (3 examples): SIMD, Matrix multiplication
    - effects/ (3 examples): Algebraic effects demonstrations
    - modules/ (3 examples): Module system examples
    - gpu/ (3 examples): GPU FFT and parallel computing
    - advanced/ (3 examples): JIT compilation, Turing machines
  - Comprehensive README files for each category with explanations
  - Cross-references to tutorials and reference documentation
  - Progressive difficulty from basic to advanced concepts

### Documentation Structure Created
```
docs/
├── README.md - Main documentation hub with navigation
├── getting-started.md - Installation and first program guide
├── language/ - Complete language reference
│   ├── README.md - Language overview and navigation
│   └── overview.md - Language philosophy and design
├── library/ - Standard library documentation
│   ├── README.md - Library overview and organization
│   └── overview.md - Library introduction
├── tutorials/ - Step-by-step learning guides
│   ├── README.md - Tutorial index and learning paths
│   ├── beginner.md - Basic concepts and syntax
│   ├── intermediate.md - Modules, patterns, error handling
│   └── advanced.md - Effects, graphics, performance
├── reference/ - Quick reference materials
│   ├── README.md - Reference index
│   └── api.md - Complete API documentation
└── examples/ - Organized example gallery
    ├── README.md - Examples overview and navigation
    ├── basic/README.md - Basic examples guide
    ├── data-structures/README.md - Data structure examples
    ├── algorithms/README.md - Algorithm implementations
    ├── graphics/README.md - Graphics programming examples
    ├── performance/README.md - Performance optimization examples
    ├── effects/README.md - Algebraic effects examples
    ├── modules/README.md - Module system examples
    ├── gpu/README.md - GPU computing examples
    └── advanced/README.md - Advanced programming examples
```

### Enhanced Language Features
- **Struct Memory Layout**: Complete struct support with proper field offsets
- **Field Access**: Nested field access with type resolution
- **Type Safety**: Compile-time checking for all operations
- **Memory Management**: Manual and automatic memory control
- **Effects System**: Algebraic effects and handlers
- **Module System**: Import/export functionality (ready for implementation)

### Standard Library Foundation
- **Core Types**: Enhanced integer and floating-point type support
- **Graphics Module**: Complete graphics type system with utilities
- **Math Functions**: Mathematical operations and constants
- **String Operations**: Text processing and manipulation
- **Array Operations**: Data structure utilities and algorithms
- **Testing Framework**: Unit testing and benchmarking tools

### Performance Improvements
- **C Generator Optimization**: Enhanced type mapping and code generation
- **Memory Efficiency**: Proper type sizes and alignment
- **Compilation Speed**: Improved parsing and code generation
- **Runtime Performance**: Optimized struct field access and memory layout

### Quality Assurance
- **Test Suite**: All 101 tests passing with comprehensive coverage
- **Documentation**: Complete, professional documentation with examples
- **Code Quality**: Clean, organized codebase with proper structure
- **Developer Experience**: Professional project organization and tools

### Statistics
- **110 files changed** in this release
- **13,615 insertions, 80 deletions**
- **27 working examples** across 9 categories
- **Complete documentation** rivaling major languages
- **Full type system** with proper integer support

## [0.6.0] - 2026-01-08

### 🚀 Major Release - Import/Export System & GPU Integration

### Added
- **Complete Import/Export System**
  - Full module system with export declarations
  - Import statement resolution with circular import detection
  - Module symbol tracking and validation
  - Standard library integration with math module
  - Relative and absolute import paths
  - Export control for public vs private symbols

- **Multi-Backend GPU Integration**
  - CUDA backend for NVIDIA GPUs
  - OpenCL backend for cross-platform GPU support
  - Metal backend for Apple Silicon/Mac (optimized for M1/M2/M3)
  - Auto-detection of best available GPU backend
  - GPU runtime with memory management and data transfer
  - GPU shader compilation (CUDA PTX, OpenCL, Metal MSL)

- **Apple Silicon Metal Support**
  - Native Metal framework integration
  - Metal Shading Language (MSL) code generation
  - xcrun-based Metal shader compilation
  - Unified memory architecture optimizations
  - Apple Silicon-specific performance tuning

- **Enhanced Module System**
  - ModuleResolver with dependency tracking
  - Symbol collision detection and resolution
  - Circular import detection and reporting
  - Export validation and symbol management
  - Module information and analysis tools

- **GPU Runtime Library**
  - Cross-platform GPU backend abstraction
  - Memory allocation and management
  - Data transfer between host and device
  - Kernel launch and synchronization
  - Performance benchmarking tools

- **GPU Code Generation**
  - CUDA C kernel generation from FLOW functions
  - OpenCL kernel generation
  - Metal Shading Language generation
  - Type mapping between FLOW and GPU languages
  - Kernel parameter handling

### Enhanced Language Features
- **Print Function**: Added proper print() intrinsic support in C generator
- **Module Integration**: Enhanced transpiler with module resolution
- **GPU Compilation**: GPU backend selection and compilation
- **Performance Tools**: GPU vs CPU benchmarking capabilities

### New Examples
- **Import/Export Demo**: Complete module system demonstration
- **Metal GPU Demo**: Apple Silicon GPU integration example
- **GPU Integration Demo**: Multi-backend GPU computing example
- **Math Module**: Comprehensive standard library module

### Documentation
- **Module System**: Complete import/export documentation
- **GPU Integration**: Multi-backend GPU programming guide
- **Metal Support**: Apple Silicon optimization documentation
- **Standard Library**: Module development guidelines

### Statistics
- **3 New GPU Backends**: CUDA, OpenCL, Metal
- **Complete Module System**: Import/export with validation
- **Apple Silicon Optimized**: Metal backend for M-series chips
- **Cross-Platform GPU**: Automatic backend detection
- **Enhanced Toolchain**: GPU compilation and execution

### Platform Support
- **macOS**: Full Metal support with Apple Silicon optimization
- **Linux**: CUDA and OpenCL backend support
- **Windows**: CUDA backend support (OpenCL planned)
- **Cross-Platform**: Automatic GPU backend detection

## [0.9.0] - 2026-08-05

### Consolidation release

Every open branch, worktree, stash, and PR merged into `main`; the repository
now has a single branch tagged `v0.9.0`.

### Added
- **Go-style concurrency runtime** — fibers, channels (`Chan<T>` with monomorphization), select, work stealing, netpoll, multi-shot continuations, TLS/HTTPS accept loop, HTTP over fibers. C kernels under `runtime/`, Flow wrappers under `lib/runtime/`, 25 examples under `examples/concurrency/`.
- **Package registry** — `registry/` with 16 seed packages and ecosystem demo projects.
- **Pipeline `choose`** — state-driven stage selection: `x |> choose sel { A => f, B => g }`.
- **VS Code extension 0.3.0** — debug adapter, test explorer, snippets, file icon, published under the `quilio` Open VSX namespace; `flow-pack` and `flow-themes` companions.
- **Recorded demo gallery** — headless `./flow record` backend and GIFs regenerated from the real programs.
- Runtime-in-Flow build wiring (`flow_runtime_flow_sources`), `FLOW_CFLAGS` / `FLOW_TSAN` overrides, OpenSSL and OpenMP probes.

### Changed
- **Stricter type checking** — `let` immutability enforced (use `let mut`), bool vs i32 distinction, overload arity checks; corpus updated.
- LANGUAGE_SPEC refreshed to match shipped surfaces; spec version now tracks the release.
- Version metadata aligned to **0.9.0** (`flow.toml`, `pyproject.toml`, wiki hero).

### Notes
- flowc self-hosting is through Phase D slice 1 (pip-free Stage-A compile in CI); Python remains the production compiler.
- Known strict-checker gaps carry `flow:lenient` pragmas with board cards (generic channel intrinsics, string vs byte-buffer coercions, capability parameters).

## [0.8.0] - 2026-08-05

### Official public release

First annotated git tags and GitHub Releases for Flow. Documentation ships from
[GitHub Pages](https://flooooooooooow.github.io/flow/). VPS wiki deploy is disabled.

### Added
- **Self-hosting bootstrap (`flowc`)** — Flow-written Stage-A compiler under `compiler/` (lexer, parser, AST, cgen, typecheck, resolve, roundtrip/self-emit). Plan: `docs/project/self-hosting.md`.
- **Declarative ordering** — `xs |> sort` / `sortBy` (Phase 1).
- **GPU / unified memory** + fill-shader surface language.
- **Dynamics namespaces**, connect composition, `always`/`never` constraints, units, RK4 solver path.
- **GitHub Pages** wiki deploy (`.github/workflows/wiki.yml`); community files (`CODE_OF_CONDUCT`, `SECURITY`, `CITATION.cff`).
- **Homebrew tap** packaging (when `packaging/homebrew` lands on `main`)
### Changed
- Docs homepage and badges point at `flooooooooooow/flow`.
- Version metadata aligned to **0.8.0** (`flow.toml`, `pyproject.toml`, wiki hero).

### Notes
- Production compiler remains Python (`src/flow/`) with `flowc` as the self-host ladder (Phases A–E on the roadmap).
- Prior unreleased notes below are folded into this cut.

## [0.7.0] - 2026-02-09

### Security Audit & Hardening

A comprehensive security and quality audit was performed across the entire codebase.
98 issues were filed and systematically triaged. As of Feb 10, 2026, all 98 have been resolved (100%).

### Fixed - Critical Security
- **CLI shell injection** (#83): Unquoted variable interpolation in the `flow` shell script allowed arbitrary command execution. Fixed by using argument arrays and avoiding shell interpolation.
- **Runtime command injection** (#72): `std::system()` in Vulkan shader compilation allowed command injection. Replaced with `execvp`-based `runCommand`.
- **Module resolver path traversal** (#44): Import statements could traverse outside the project directory. Added path validation.

### Fixed - Compiler
- **MLIR generator**: Fixed 7 bugs including undefined `total_size` crash (#31), incorrect `memref.load` syntax (#32), string literal crash (#33), invalid module-scope constants (#35), missed returns in if-else (#36), undefined `%c0` in unary minus (#37), SSA names in dense attributes (#38, #39).
- **Module resolver**: Fixed circular import silent drops (#45), symbol collision drops (#46), missing import warnings (#47), stub `_resolve_symbols` (#48).
- **Monomorphize**: Fixed `VarDecl` losing `is_mutable` flag (#52), ambiguous name mangling (#51), deepcopy performance (#53).
- **Parser**: Fixed fragile return-value heuristic (#3), `EffectCall` modeling for dotted methods (#4).
- **C generator**: Fixed `remove_outer_parens` (#24), for-loop always using `<` (#25), dead code behind `if False` (#30), `bool` mapped to `int32_t` (#29).
- **Transpiler**: `--strict` flag no longer a no-op (#43).

### Fixed - Standard Library
- **macOS POSIX constants** (#65): `O_CREAT`, `O_TRUNC`, etc. corrected for macOS (differ from Linux).
- **AF_INET6** (#68): Corrected for macOS.
- **format_hex_ptr** (#67): No longer truncates 64-bit pointers.
- **memory_pool_create** (#66): Now checks `malloc` return value.
- **Collection constructors** (#63): No longer initialize data to null.
- **Alignment functions** (#71): Now validate power-of-two.
- **pthread externs** (#70): Corrected from `ptr<i8>` to proper mutex types.
- **Atomic operations** (#69): Expanded beyond i32-only.

### Fixed - CLI & Tooling
- **Predictable temp directories** (#84): Now uses secure random temp paths.
- **Missing `set -euo pipefail`** (#85): Added to shell scripts.
- **No `.flow` extension validation** (#86): CLI now validates file extensions.
- **Hardcoded LLVM path** (#87): Now respects environment configuration.

### Fixed - Testing
- **Temp file leaks** (#94): `delete=False` temp files now cleaned on failure.
- **Bare `except: pass`** (#97): Replaced with specific exception handling.
- **Unused hypothesis dependency** (#96): Removed.
- **Duplicate test files** (#98): Consolidated.
- **Partial ERROR_CASES/EDGE_CASES** (#95): Now fully exercised.

### Fixed - Runtime
- **debugCallback null dereference** (#80): Added null check.
- **Vulkan resource leak on init failure** (#79): Resources now freed on error paths.

### Known Open Issues

**All critical issues are closed** and tracked on GitHub for history.

See the [GitHub Issues](https://github.com/flooooooooooow/flow/issues) page for full details.

### Statistics
- **98 audit issues** filed across compiler, stdlib, runtime, CI, and testing
- **98 issues resolved** (100% closure rate)
- **0 issues open**
- **All testing issues resolved** (5/5)
- **All CLI issues resolved** (5/5)
- **All runtime issues resolved** (6/6)
- **All CI issues resolved** (6/6)

## [Unreleased]

### Planned
- Self-hosting Phases B–E (`flowc` default host)
- Package registry beyond git deps
- Custom domain for docs
