# Appendix B. Feature coverage index

The index lists the public features in Flow v0.11.1. “Full” means that the
feature works with the stated compiler and backend. “Partial” marks an
important limit. “Target” requires a platform or external toolchain. “Planned”
means that the syntax or design is not implemented.

## Lexical rules and operators

| Feature | Status | Book location |
|---|---|---|
| identifiers, whitespace, braces, statements | Full | Chapters 1–3 |
| `#` line comments | Full; C and block comments unsupported | Chapter 1 |
| decimal and hexadecimal integers | Full | Chapters 2, 8 |
| binary integer literals | Planned; not lexed | Appendix A |
| floating-point and scientific literals | Full | Chapters 2, 8 |
| Boolean, string, array, and struct literals | Full | Chapters 2, 5 |
| arithmetic `+ - * / %` | Full | Chapter 2 |
| comparison `== != < > <= >=` | Full | Chapters 2, 8 |
| logical `and or not`, <code>&amp;&amp; &#124;&#124; !</code> | Full | Chapters 2, 9 |
| bitwise <code>&amp; &#124; ^ ~ &lt;&lt; &gt;&gt;</code> | Full | Chapter 9 |
| assignment `=` | Full | Chapter 2 |
| ranges `to`, `..`, `step` | Full | Chapters 3, 9 |
| pipeline <code>&#124;&gt;</code> and placeholder `_` | Full with Python host | Chapters 6, 9 |
| address-of `&` and dereference `*` | Full with C backend | Chapter 10 |
| type arrow `->`, match arrow `=>` | Full | Chapters 4, 9 |
| effect scope `::` / effect call spelling | Full with parser-specific spellings | Chapter 12 |
| field access `.` and indexing `[]` | Full | Chapters 5, 10 |

## Types

| Feature | Status | Book location |
|---|---|---|
| `i8 i16 i32 i64`, `u8 u16 u32 u64` | Full | Chapters 2, 8 |
| `i128`, `u128` | C target; MLIR gap | Chapter 8 |
| `f32`, `f64` | Full | Chapters 2, 8 |
| IEEE comparison and total sort order | Full | Chapter 8 |
| `c64`, `c128` and complex built-ins | C target | Chapter 8 |
| `bool`, `string`, `void` | Full | Chapters 2, 8 |
| fixed arrays `array<T,N>` | Full | Chapter 5 |
| dynamic arrays `array<T>` | Full; ownership is explicit | Chapters 8, 10 |
| structs and nested structs | Full | Chapter 5 |
| pointers `ptr<T>` and `null` | C target | Chapter 10 |
| SIMD `vec<T,N>` and vector literals | Partial | Chapter 14 |
| spans `span<T>`, `span<mut T>` | Full with concrete elements and C backend | Chapter 10 |
| static spans `span<T,N>` | Full with concrete elements and C backend | Chapter 10 |
| span sugar `&[T]`, `&mut [T]`, `&[T;N]` | Full | Chapter 10 |
| inferred/bare spans | Planned | Chapter 8 |
| function and closure types | Full with C backend | Chapters 4, 9 |
| raw C function pointers `cfn(...) -> R` | Python host with C backend | Chapter 11 |
| transparent aliases | Full | Chapter 8 |
| nominal `distinct type` | Full | Chapter 8 |
| explicit `as` casts | Full | Chapters 2, 8 |
| units and dimensional checking | Python host with C backend | Chapters 8, 13 |
| generic structs and functions | Full with explicit instantiation; inference gap | Chapter 8 |
| function overload resolution and mangling | Full | Chapters 8, 11 |
| traits and `impl` | Partial semantics | Chapter 8 |
| enums and tags | Full with C backend | Chapters 8, 9 |

## Declarations and attributes

| Feature | Status | Book location |
|---|---|---|
| functions and typed parameters/results | Full | Chapter 4 |
| build guards `@only`, `@guard`, `@compile` | Full Python host | Chapters 8, 16 |
| local `let`, inference, `let mut` | Full | Chapter 2 |
| `const` | Full | Chapter 8 |
| top-level mutable statics | C target; MLIR gap | Chapter 8 |
| structs | Full | Chapter 5 |
| enums | Full with C backend | Chapter 8 |
| traits and implementations | Partial | Chapter 8 |
| `extern` and variadic externs | Full with C backend | Chapter 11 |
| `@cImport` | Python host with C backend | Chapter 11 |
| `@cInclude` and opaque `extern type` | Python host with C backend | Chapter 11 |
| `@cEmbed` raw C | Python-hosted C escape hatch | Chapter 11 |
| `@inline`, `@always_inline`, `@noinline` | C target | Chapter 8 |
| `@target` | Target-dependent C attribute | Chapter 8 |
| `@flow_api` | C ABI | Chapters 8, 11 |
| `@gpu` | Metal code generator | Chapters 8, 15 |
| `@rt_safe` | Full static call-graph check with stated gaps | Chapter 10 |
| `@lifetime` | Full v0 checker with stated gaps | Chapter 10 |
| `@safe`, `@unsafe` | Full C safety boundary with stated FFI limits | Chapter 17 |
| `dbg` | C diagnostic; MLIR evaluation only | Chapters 8, 17 |
| `expect` | C abort; MLIR evaluation only | Chapters 8, 17 |
| `test` blocks | Partial; no automatic invocation | Chapters 8, 17 |

## Expressions and statements

| Feature | Status | Book location |
|---|---|---|
| literals, variables, calls, field/index access | Full | Chapters 2–5 |
| unary and binary expressions | Full | Chapters 2, 9 |
| struct and array construction | Full | Chapter 5 |
| closures and by-value capture | C target; MLIR gap | Chapter 9 |
| escaping closures and higher-order calls | C target | Chapter 9 |
| value-producing `if` | Full C/MLIR | Chapter 9 |
| `if`, `elif`, `else` statements | Full | Chapter 3 |
| `while` | Full | Chapter 3 |
| `for` with `to`, `..`, `step` | Full | Chapter 3 |
| `parallel for` | OpenMP or serial; MLIR serial | Chapters 9, 12 |
| `return`, early return | Full | Chapters 1, 4 |
| `break`, `continue` | Full except noted match/C edge | Chapter 9 |
| `defer` | Full C/MLIR | Chapter 9 |
| match literals and default | Full | Chapter 9 |
| match bindings, wildcard, guards, alternation | Full with C backend | Chapter 9 |
| match struct and fixed-list patterns | Full with C backend | Chapter 9 |
| Boolean/enum exhaustiveness | Full; integer checking limited | Chapter 9 |

## Declarative data flow

| Feature | Status | Book location |
|---|---|---|
| ordinary call pipelines | Full Python host | Chapter 6 |
| placeholder argument placement | Full Python host | Chapter 6 |
| named and inferred fork records | Full Python host | Chapter 9 |
| `choose` pipeline stage | Full Python host | Chapter 9 |
| `sort`, descending, unique | Full with Python host and C backend | Chapter 9 |
| `sortBy` field ordering | Full with Python host and C backend | Chapter 9 |
| `find` | Full with Python host and C backend | Chapter 9 |
| sort/search plan selection | Full | Chapters 9, 17 |
| ordering hints and cost constraints | Full | Chapters 9, 17 |
| stable/unstable modifier distinction | Partial; all plans currently stable | Chapter 9 |
| GPU/SIMD/entropy/compact sort modifiers | Parsed without special plans | Chapter 9 |

## Effects and concurrency

| Feature | Status | Book location |
|---|---|---|
| effect declarations and operations | Full with C backend | Chapter 12 |
| capabilities | Full, stateless | Chapter 12 |
| nested and multiple handlers | Full with C backend | Chapter 12 |
| dynamic handler restoration | Full with C backend | Chapter 12 |
| effect rows | Full under strict-effects mode | Chapter 12 |
| zero/no-op unhandled compatibility | Full default; strict mode available | Chapter 12 |
| pthread threads, mutex, condvar, semaphore, once | Native target | Chapter 12 |
| WaitGroup | Native target | Chapter 12 |
| buffered channels and close | Native target | Chapter 12 |
| nonblocking channel operations | Native target | Chapter 12 |
| `select2`, `select4`, default/try forms | Native target | Chapter 12 |
| simulated async handler | Full deterministic implementation | Chapter 12 |
| threaded async handler | Native pthread target | Chapter 12 |
| M:N fiber handler and work stealing | Darwin/Linux native target | Chapter 12 |
| blocking async I/O | Native POSIX target | Chapter 12 |
| kqueue/epoll netpoll | Darwin/Linux target | Chapter 12 |
| TCP effect and blocking TCP | Native target | Chapter 12 |
| general Flow-frame delimited continuations | Partial/scaffold | Chapter 12 |
| `async`/`await` syntax | Planned, deliberately absent | Chapter 12 |

## Modules, packages, and interoperation

| Feature | Status | Book location |
|---|---|---|
| logical imports and selected symbols | Full Python host | Chapter 11 |
| aliases and sibling imports | Full Python host | Chapter 11 |
| exports and export lists | Full | Chapter 11 |
| re-export | Python host; self-hosted gap | Chapter 11 |
| module resolution via `[paths]` | Full | Chapter 11 |
| `module` blocks | Partial; flattened, not namespaces | Chapter 11 |
| `flow.toml` project builds | Full | Chapter 11 |
| registry, path, and Git dependencies | Full in the local package client | Chapter 11 |
| version requirements and lock file | Direct-dependency support | Chapter 11 |
| hosted publish/accounts/yank service | Planned | Chapter 11 |
| native project sources and libraries | Full; target-dependent | Chapter 11 |
| stable C/WASM export aliases | Full with C backend | Chapter 11 |
| Python wheels | Target-dependent; type restrictions | Chapters 11, 16 |

## Evolution and dynamics

| Feature | Status | Book location |
|---|---|---|
| `flow`, state, parameters | Full with Python host and C backend | Chapters 7, 13 |
| inputs and outputs | Full with Python host and C backend | Chapter 13 |
| `evolves as` derivatives | Full with Python host and C backend | Chapters 7, 13 |
| Euler and RK4 solver selection | Full | Chapters 7, 13 |
| time units in solver declarations | Full in the evolution expander | Chapter 13 |
| sampled `every` / `becomes` | Full in the evolution expander | Chapter 13 |
| `when ... reaches` hybrid reset | Full in the evolution expander | Chapter 13 |
| `always` runtime invariants | Full in the evolution expander | Chapter 13 |
| nested flows and `connect` | Full Stage 1 implementation; input limits noted | Chapter 13 |
| phase-portrait representation | Full in evolution graphics | Chapter 13 |
| explicit linear representation | Full; automatic Jacobian planned | Chapter 13 |
| `dsys` state-space declarations | Full in the dynamics expander | Chapter 13 |
| controllability/observability/spectral sense | Full in library and expander | Chapter 13 |
| LQR | Full discrete implementation | Chapter 13 |
| GA controller search/report | Full in supplied example | Chapter 13 |
| fields, boundary, Laplacian | Full 1-D implementation | Chapter 13 |

## Numeric and domain libraries

| Feature family | Status | Book location |
|---|---|---|
| math and complex helpers | Full with C backend and library | Chapters 8, 14 |
| arrays, collections, strings, text, option, result | Library | Chapters 5, 6; Appendix D |
| vectors, matrices, BLAS/LAPACK | Library/target-dependent | Chapter 14 |
| forward autodiff | Library | Chapter 14 |
| reverse tape autodiff | Library | Chapter 14 |
| generated gradients | Generator and library | Chapter 14 |
| tensor and neural-network operations | Library; backend-dependent | Chapter 14 |
| optimisers and ML command family | Library and MLIR | Chapter 14 |
| statistics, FMM, circuits, dynamics | Library | Chapter 14; Appendix D |
| checked arithmetic and big integers | Library | Appendix D |

## Media and device surfaces

| Feature | Status | Book location |
|---|---|---|
| native 2D graphics and input | macOS/Linux/Windows target | Chapter 15 |
| headless frame/GIF recording | Full with supported graphics backend | Chapter 15 |
| fill shader language | Metal and C shader backends | Chapter 15 |
| `@gpu` Metal compute generation | macOS target | Chapter 15 |
| Metal GPU memory helpers | macOS target | Chapter 15 |
| WGSL/WebGPU crossing | Browser target | Chapters 15, 16 |
| software 3D rendering | Library/native graphics | Chapter 15 |
| UI layout functions | Library | Chapter 15 |
| UI layout syntax sugar | Partial/host-dependent | Chapter 15 |
| audio runtime and compile wrapper | Native target | Chapter 15 |
| audio DSP, graph, WAV, synth, filters | Library | Chapter 15; Appendix D |
| Vulkan demos and Flow wrappers | Target-dependent | Chapter 15 |
| CUDA and OpenCL | Not shipped | Chapter 15 |

## Compilation and tooling

| Feature | Status | Book location |
|---|---|---|
| self-hosted Stage-A compiler | Core subset | Chapters 1, 16 |
| Python-hosted compiler | Broadest feature support | Chapters 1, 16 |
| C backend | Primary | Chapter 16 |
| MLIR backend | Partial parity | Chapter 16 |
| JIT | MLIR toolchain | Chapter 16 |
| WebAssembly/Emscripten | Target-dependent | Chapter 16 |
| Python wheel | Target-dependent | Chapters 11, 16 |
| tutorial JavaScript runner | Core teaching subset | Chapter 16 |
| formatter and REPL | Full tool commands | Chapter 17 |
| native debugger and DAP | Target-dependent | Chapter 17 |
| LSP and VS Code extension | Tooling | Chapter 17 |
| tiered tests and runtime suites | Full | Chapter 17 |
| UBSan, ASan, TSan | Toolchain-dependent | Chapter 17 |
| safety profile | Full C profile | Chapter 17 |
| MISRA/CERT scans | Modelled-rule scanners | Chapter 17 |
| WCET/stack analysis | Partial static analysis | Chapter 17 |
| explainable plan selection | Full selected constructs | Chapter 17 |
| FIR-G graph and analyses | Compiler tool | Chapter 17 |
| reproducible-build guidance | Process/tooling | Chapter 17 |
| theorem and claim syntax | Partial | Chapter 17 |
| Flow-specific challenge checker | Syntax rules plus compile/run | Chapter 19 |
