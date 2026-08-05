# Flow: How the Language Works (and Why MLIR)

Flow is a statically typed, compiled language that sits at the intersection of systems programming, ML workloads, audio, and graphics. It is implemented primarily in Python and targets multiple backends. MLIR is one of the targets, not the whole story: Flow also has a portable C backend and a Metal shader pipeline. The approach is intentionally pragmatic: keep the language semantics small, expressible, and easy to lower, while still providing powerful capabilities like algebraic effects and automatic differentiation.

This writeup explains the structure and the design choices as they exist in this codebase.

## 1. Core Architecture

Flow is a classic front end with multiple back ends:

1. **Parser** (`src/flow/parser.py`) lexes and parses `.flow` source into an AST.
2. **Type checking** (`src/flow/type_checker.py`) performs semantic checks and type inference in a mostly conventional static type system.
3. **Lowering** chooses a backend:
   - **C generator** (`src/flow/c_generator.py`) for portable native compilation via Clang/GCC.
   - **MLIR generator** (`src/flow/mlir_generator.py`) for more advanced pipelines and JIT.
   - **Metal codegen** (`src/flow/metal_codegen.py`) for GPU shader generation.

The CLI (`flow` bash script and `src/flow/transpiler.py`) orchestrates these flows and exposes commands like `run`, `compile`, `mlir`, `mlir-run`, `jit`, and `gpu`.

## 2. Language Surface and Type System

The language is deliberately small and readable:

- **Primitives**: `i32`, `i64`, `f32`, `f64`, `bool`, `string`, `void`
- **Pointers**: `ptr<T>` and `ptr<void>` for low-level interop
- **Arrays**: fixed-size `array<T, N>`
- **Structs**: named aggregates
- **Type aliases**: `type Name = ...` for readable, reusable type expressions
- **Distinct types**: `distinct type UserId = i64` for nominal safety over primitives
- **Generics**: functions may be parameterized by type variables

The parser and type checker are typical for a small language: parse to AST, infer and check types, then lower. Generics are handled by a monomorphization pass (`src/flow/monomorphize.py`).

## 2.1 Monomorphization Safety

To avoid infinite generic expansion, the monomorphizer enforces a depth guard and
fails fast when recursive instantiation grows without bound. This is a compiler
safety valve rather than a semantic restriction.

## 2.2 Type Aliases, Distinct Types, and Casts

Type aliases are purely syntactic and lower away, while distinct types introduce
nominal boundaries without changing runtime layout. This gives a pragmatic mix:
readable signatures for humans and safer identifiers for large systems. Casts
via `as` are explicit and controlled (e.g., `UserId as i64`) when you want to
cross those boundaries intentionally.

## 3. Algebraic Effects: The Semantic Anchor

Flow includes algebraic effects and capabilities as first-class language constructs. This is not a surface feature; it shapes the way programs are composed.

- **Effects** declare what operations can be performed.
- **Capabilities** provide implementations for those operations.
- Call sites can be decoupled from implementations, allowing effect handlers to be swapped without rewriting core logic.

This is a design choice: the language enforces a separation between what a program *needs* and how it is *provided*. It makes side effects explicit, which matters for correctness and for later transformations.

## 4. Automatic Differentiation as a Language Feature

Autodiff is built into the standard library and language ecosystem, not bolted on as a separate tool. It is used for machine learning and optimization workloads. This reflects a core intent: Flow is a language for numerical programming where gradients are a first-class concern.

## 5. MLIR: Why It Exists Here

MLIR is used as a backend, not as a replacement for the language. The approach is:

- **Front end is independent** (Flow AST remains the source of truth).
- **Lowering targets MLIR** when the user wants JIT or MLIR-native tooling.
- **Lowering targets C** when the user wants maximum portability.

This is a practical split: MLIR enables richer pipelines (e.g., JIT or future GPU lowering), while C is a stable, portable fallback that requires no LLVM installation.

## 6. The C Backend: Portable, Predictable Output

The C backend is a deliberate design choice. It provides:

- A minimal, predictable compilation target.
- Easy integration with native toolchains and debugging.
- A stable fallback path when MLIR is unavailable.

The compiler emits C with standard library calls and a small runtime layer. This makes it possible to compile Flow code nearly anywhere a C compiler exists.

## 7. Runtime, Stdlib, and Concurrency

Flow is not “just a compiler.” It includes a small runtime and native support:

- `runtime/` includes a macOS graphics backend (`gfx_macos.m`).
- The standard library exposes memory, math, concurrency, and system modules.
- The CLI exposes `build-native` and `run-native`, enabling mixed Flow + native sources.

The concurrency stdlib is intentionally minimal but now includes real synchronization
primitives backed by pthreads and atomics. Mutexes and rwlocks store opaque backing
storage and call into `pthread_*`, and spinlocks/once/waitgroups use atomic operations.
Channels allocate real buffers and initialize a lock for coordination.

There is an explicit path for real-world integration, not just toy programs.

## 8. Tooling and Developer Experience

The project ships with:

- A CLI front end (`flow`)
- An LSP server (`flow-lsp`)
- A REPL
- A VS Code extension (`third_party/integrations/vscode`)
- **Guarded builds**: decorators like `@only("hot")` or `@compile` allow
  selectively including declarations in hot-reload, JIT, or full compile modes

This is significant: it signals a commitment to a usable language, not a research-only artifact.

## 9. Project Status (Feb 2026)

The v0.7.0 audit backlog listed in `docs/project/issues-checklist.md` has been fully worked
through in this snapshot, including CI hardening, security scanning, and
compiler correctness fixes. The roadmap in `docs/NEXT.md` reflects the next
frontier rather than the audit cleanup.

## 10. Summary: The Approach in One Line

Flow is a small, statically typed language with algebraic effects and autodiff, compiled through a straightforward AST pipeline into either C or MLIR, backed by a minimal runtime and real tooling. The “MLIR-based language” label is accurate, but incomplete; the real design is about preserving explicit semantics while giving multiple lowering targets.

In other words: the interesting part is not that MLIR is used, but that the language is built to make multiple backends possible without changing the semantics.
