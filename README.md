# Flow Programming Language

[![CI](https://github.com/abhishekshivakumar/transpile/actions/workflows/ci.yml/badge.svg)](https://github.com/abhishekshivakumar/transpile/actions/workflows/ci.yml)

<img src="docs/assets/flow-mascot.png" alt="Flowy the Hedgehog" width="180" align="right">

A statically-typed, compiled language for describing **systems that evolve through time** — with **algebraic effects**, **automatic differentiation**, **native dynamics/control analysis**, and **native graphics**.

> **Why Flow exists:** see [VISION.md](VISION.md) — evolution as the primary abstraction.

```flow
function main() -> i32 {
    println("Hello, Flow!")
    return 0
}
```

```bash
./flow run hello.flow
```

---

## Project Statistics

| Metric | Count |
|--------|-------|
| **Total Lines of Code** | ~38,000 |
| Flow source files | ~1,180 example/app programs; compiler + stdlib in tree |
| Python compiler | 44 modules under `src/flow/` |
| Standard library | 48 top-level `lib/stdlib/*.flow` (+ nested audio/ui/…) |
| Tests | ~217 `.py` / `.flow` under `tests/` |
| Examples compile status | 986/1193 pass (see `examples/STATUS.md`) |

---

## Quick Start

```bash
git clone https://github.com/flooooooooooow/flow.git
cd flow
./flow run examples/basics/hello_world.flow
```

**Requirements:** Python 3.9+, Clang or GCC

---

## Directory Structure

```
flow/
│
├── flow                    # CLI entry point (bash script)
├── flow-lsp                # Language Server Protocol launcher
├── README.md               # This file
├── ROADMAP.md              # Development roadmap
├── VISION.md               # Founding vision
├── CONTRIBUTING.md         # Collaboration guide
├── LICENSE                 # MIT License
├── Makefile                # Build automation
│
├── docs/project/           # Project meta (questions, issue checklist, writeups)
├── wasm/                   # WebAssembly toolchain + demos
│
├── src/flow/               # COMPILER (Python, 12k lines)
│   ├── parser.py           # Lexer + Parser → AST (1.9k lines)
│   ├── type_checker.py     # Semantic analysis (580 lines)
│   ├── c_generator.py      # Flow → C codegen (1.4k lines)
│   ├── mlir_generator.py   # Flow → MLIR codegen (2.4k lines)
│   ├── transpiler.py       # CLI commands
│   ├── lsp_server.py       # IDE support
│   ├── repl.py             # Interactive mode
│   ├── monomorphize.py     # Generics instantiation
│   ├── gpu_integration.py  # GPU abstraction
│   ├── metal_codegen.py    # Metal shader generation
│   └── ...
│
├── lib/stdlib/             # STANDARD LIBRARY (34 modules)
│   ├── autodiff.flow       # Automatic differentiation
│   ├── nn.flow             # Neural network layers
│   ├── gfx.flow            # Graphics API
│   ├── math.flow           # Math functions
│   ├── memory.flow         # Memory utilities
│   ├── concurrent.flow     # Threads, atomics
│   ├── audio.flow          # Audio processing
│   └── ...
│
├── runtime/                # NATIVE RUNTIME
│   └── gfx_macos.m         # macOS graphics backend (230 lines)
│
├── examples/               # EXAMPLES (62 programs, 12k lines)
│   ├── basics/             # Hello world, fibonacci, sorting (12 files)
│   ├── games/              # Tetris, 2048 with graphics (7 files, 4.7k lines)
│   ├── ml/                 # Machine learning framework (4 files)
│   ├── neural_networks/    # Autodiff, backprop (6 files)
│   ├── effects/            # Algebraic effects demos (3 files)
│   ├── linalg/             # Linear algebra (2 files)
│   ├── numerical/          # ODE solvers, optimization (2 files)
│   ├── systems/            # Memory pools, hash tables (3 files)
│   ├── gpu/                # GPU/SIMD examples (8 files)
│   ├── generics_traits/    # Generic programming (9 files)
│   ├── graphics/           # Rendering, shaders (3 files)
│   ├── crypto/             # SHA-256 (1 file)
│   ├── data/               # CSV parsing (1 file)
│   └── compilers/          # Expression calculator (1 file)
│
├── benchmarks/             # PERFORMANCE BENCHMARKS
│   ├── micro/              # Matrix multiply, FFT, N-body, sort, Mandelbrot
│   ├── runner.flow         # Benchmark harness
│   └── README.md
│
├── apps/                   # COMPLETE APPLICATIONS
│   ├── flowdb/             # Key-value database
│   └── flow-http/          # HTTP server framework
│
├── tests/                  # TEST SUITE (85 tests)
│   ├── core/               # Core language tests
│   ├── runtime/            # Runtime behavior tests
│   ├── stdlib/             # Standard library tests
│   └── ...
│
├── docs/                   # DOCUMENTATION
│   ├── assets/             # Mascot, images
│   ├── getting-started.md  # Quick start guide
│   ├── LANGUAGE_SPEC.md    # Full language reference
│   ├── grammar.ebnf        # Formal grammar
│   ├── language/           # Language feature docs
│   ├── library/            # Stdlib reference
│   ├── tutorials/          # Beginner → Advanced
│   └── playground/         # Web playground (syntax explorer)
│
├── third_party/            # THIRD-PARTY INTEGRATIONS
│   └── integrations/       # Editor + tooling integrations
│       └── vscode/         # VS Code extension
│
├── tools/                  # DEVELOPMENT TOOLS
│   ├── flow_grad_flow.py   # Gradient code generator
│   ├── flow_jit_pipeline.py
│   └── ...
│
├── scripts/                # BUILD SCRIPTS
│   ├── run_examples.sh
│   └── ...
│
├── wasm/                   # WEBASSEMBLY toolchain + browser gallery
│   └── ...
│
├── demos/                  # Runnable graphics / Vulkan demos
│   └── ...
│
└── site/                   # Custom wiki shell (HTML/CSS/JS; not MkDocs output)
    └── ...
```

---

## Language Features

### Core Syntax

```flow
# Variables
let x: i32 = 42              # Immutable
let mut counter: i32 = 0     # Mutable

# Functions
function add(a: i32, b: i32) -> i32 {
    return a + b
}

# Structs
struct Point { x: f32, y: f32 }
let p: Point = Point { x: 1.0, y: 2.0 }

# Control flow
if x > 0 { ... } elif x < 0 { ... } else { ... }
while condition { ... }
for i in 0 to 10 { ... }
```

### Type System

```
Primitives:  i32, i64, f32, f64, bool, string, void
Pointers:    ptr<T>, ptr<void>
Arrays:      array<T, N>  (fixed-size)
Structs:     struct Name { field: Type }
Generics:    function identity<T>(x: T) -> T
```

### Algebraic Effects (Unique Feature)

```flow
effect Logger {
    log(msg: string) -> void
}

capability ConsoleLogger {
    effect Logger
    function log(msg: string) -> void {
        println(msg)
    }
}

# Swap implementations without changing code
```

See the full walkthrough in [docs/effects-showcase.md](docs/effects-showcase.md)
(`examples/effects/showcase.flow` — compiles, links, and runs end to end).

### Automatic Differentiation

```flow
# Library autodiff (not a compiler pass): dual numbers + reverse helpers
# See docs/library/autodiff.md — used for neural nets, optimization, physics
# Demo: examples/ml/models/mlp_xor.flow
```

### FFI (C Interop)

```flow
extern {
    function malloc(size: i64) -> ptr<void>
    function free(p: ptr<void>) -> void
    function printf(fmt: string, ...) -> i32
}
```

---

## CLI Reference

```bash
./flow run <file>           # Compile and run
./flow compile <file>       # Compile only (output: build/)
./flow debug <file>         # Debug build + LLDB/GDB (--break / --no-launch)
./flow gfx <file>           # Native graphics (macOS / Linux+SDL2 / Windows)
./flow shader <file>        # Fill-shader demo (Metal on macOS)
./flow audio <file>         # Compile and run with audio backend
./flow python <file>        # Generate Python wheel
./flow test                 # Run test suite (lenient type-checking by default)
./flow test --strict --tier2 # Strict corpus + transpile/clang compile checks
./flow search <query>       # Package registry search
./flow add <pkg>            # Add dependency from local index / git / path
./flow version              # Print Flow version (0.3.3)
./flow fmt <file>           # Format code
./flow repl                 # Interactive mode
./flow jit <file>           # JIT compile (requires LLVM)
./flow lsp                  # Start language server (diagnostics)
```

### Python Package Generation

```bash
# Generate a Python wheel from a Flow library
./flow python mylib.flow --name mylib

# Output: dist/mylib-0.1.0-*.whl
pip install dist/mylib-*.whl
python -c "import mylib; print(mylib.add(1, 2))"
```

See [docs/python-target.md](docs/python-target.md) for details.

---

## Editor support (VS Code & Cursor)

```bash
# Local install from this repo
./scripts/publish_vscode_extension.sh --install

# Or after marketplace publish:
#   cursor --install-extension flooooooooooow.flow-language
#   code --install-extension flooooooooooow.flow-language
```

Extension lives at `third_party/integrations/vscode/flow-language/` (syntax + LSP).  
Publishing: set `VSCE_PAT` and run `./scripts/publish_vscode_extension.sh --publish` — see that folder’s `PUBLISH.md`.

## Highlighted Examples

### Games (with Native Graphics)

![Flow Tetris demo](docs/demos/tetris.gif)

```bash
# Tetris - fully playable!
./flow gfx examples/games/tetris_gfx.flow
# (or: compile + link runtime/gfx_macos.m / gfx_linux.c / gfx_windows.c)

# Regenerate the demo GIF:
#   python3 scripts/record_tetris_gif.py

# 2048 puzzle
./flow gfx examples/games/2048_gfx.flow
```

### Machine Learning

```bash
# XOR neural network (trains successfully!)
./flow run examples/ml/models/mlp_xor.flow

# Output:
# Epoch 4000: Loss = 0.000197
# 0 XOR 0 = 0.005 -> 0 [OK]
# 0 XOR 1 = 0.988 -> 1 [OK]
# SUCCESS: Network learned XOR!
```

### Benchmarks

```bash
./flow run benchmarks/micro/sort_benchmark.flow
./flow run benchmarks/runner.flow
```

### Interop & System

```bash
# System info (native helpers)
./flow run examples/system/system_info.flow

# Python embedding (CPython via framework on macOS)
./flow run examples/interop/python_embed.flow

# Matrix optimization demo (Flow-only variants)
./flow run examples/bench/matmul_optimizations.flow

# Print assembly + MLIR for matmul optimizations
./flow test-matmul

# Interop runtime test
./flow test-interop
```

---

## Compiler Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ Flow Source │ ──▶ │   Parser    │ ──▶ │     AST     │
│   (.flow)   │     │  (parser.py)│     │             │
└─────────────┘     └─────────────┘     └──────┬──────┘
                                               │
                    ┌──────────────────────────┼──────────────────────────┐
                    │                          │                          │
                    ▼                          ▼                          ▼
           ┌─────────────┐            ┌─────────────┐            ┌─────────────┐
           │ C Generator │            │    MLIR     │            │   Metal     │
           │             │            │  Generator  │            │  Codegen    │
           └──────┬──────┘            └──────┬──────┘            └──────┬──────┘
                  │                          │                          │
                  ▼                          ▼                          ▼
           ┌─────────────┐            ┌─────────────┐            ┌─────────────┐
           │   Clang     │            │    LLVM     │            │   Metal     │
           │             │            │     JIT     │            │   Shaders   │
           └─────────────┘            └─────────────┘            └─────────────┘
```

---

## Unique Selling Points

| Feature | Flow | Rust | Go | Mojo | Julia |
|---------|------|------|-----|------|-------|
| Algebraic Effects | ✅ | ❌ | ❌ | ❌ | ❌ |
| Library Autodiff | ✅ | ❌ | ❌ | ✅ | ✅ |
| C Backend (portable) | ✅ | ❌ | ❌ | ❌ | ❌ |
| Native Graphics | ✅ | ❌ | ❌ | ❌ | ❌ |
| No LLVM Required | ✅ | ❌ | ✅ | ❌ | ❌ |

---

## Comparison with C and MOJO

### Flow vs C

| Feature | Flow | C |
|---------|------|---|
| **Memory Safety** | Automatic memory management with optional manual control | Manual memory management, prone to buffer overflows and memory leaks |
| **Syntax** | Modern, expressive syntax with type inference | Verbose, low-level syntax requiring explicit type declarations |
| **Audio Programming** | Built-in audio abstractions and effects system | Requires external libraries and complex setup |
| **Type Safety** | Strong static typing with advanced type system | Weak typing with manual casting required |
| **Concurrency** | Effects + pthread channels/WaitGroup + FiberAsync (M:N) + OpenMP `parallel for` | Manual thread management and mutex handling |
| **Development Speed** | Rapid prototyping with high-level abstractions | Slower development due to low-level details |
| **Performance** | Compiles to efficient LLVM IR | Direct compilation to machine code |
| **Learning Curve** | Gentle learning curve with intuitive syntax | Steep learning curve with complex concepts |

### Flow vs MOJO

| Feature | Flow | MOJO |
|---------|------|-----|
| **Primary Domain** | Audio processing, scientific computing, systems programming | AI/ML development and data science |
| **Performance** | Optimized for real-time audio and systems performance | Optimized for AI/ML workloads |
| **Syntax** | Clean, minimal syntax inspired by Rust/Go | Python-like syntax with extensions |
| **Memory Management** | Automatic with optional manual control | Ownership model similar to Rust |
| **Hardware Acceleration** | Built-in SIMD and GPU support | Native hardware acceleration for ML |
| **Audio Processing** | First-class audio processing capabilities | Limited audio processing capabilities |
| **Scientific Computing** | Optimized for signal processing | Optimized for numerical computation |
| **Compilation** | Ahead-of-time compilation to LLVM IR | Compilation to efficient machine code |
| **Ecosystem** | Audio-focused libraries and tools | AI/ML-focused ecosystem |

### Why Choose Flow?

Flow's thesis ([VISION.md](VISION.md)) is that programs describe systems that evolve through time:

- **Evolution as the Abstraction**: Model, analyze, and control dynamical systems in one file — `dsys` plants, `sense` analysis (controllability, spectral radius, Gramians), and GA-based gain search ship today (`examples/evolution/`, `examples/dynamics/`)
- **Expressive Effects System**: Manage side effects cleanly without sacrificing performance
- **Library Autodiff**: Forward-mode dual numbers + reverse helpers / grad tools (not a compiler AD pass)
- **Real-time Audio**: A first-class domain — native DSP paths and audio abstractions with minimal latency
- **Modern Syntax**: Clean, readable code that's easy to maintain
- **Performance**: Compiles to portable C (and MLIR/LLVM) for native speed
- **Safety**: Explicit types and `@rt_safe` checks; optional manual memory

---

## Development

```bash
# Run tests (lenient by default; use --strict / test-strict for strict mode)
./flow test
./flow test --strict --tier2

# Fuzz the compiler (mutation/grammar/pipeline targets; also runs in CI)
python3 tests/fuzz/run_fuzz.py --seconds 30

# Regenerate the examples compile-status table (examples/STATUS.md)
python3 scripts/verify_examples.py

# Format code
./flow fmt examples/basics/hello_world.flow

# Start LSP for IDE support
# (go-to-definition, hover, autocomplete, inline diagnostics, find references, rename)
./flow lsp

# LSP regression harness (39 tests)
python3 scripts/test_lsp_server.py
```

### MLIR

```bash
# Generate MLIR
./flow mlir examples/basics/hello_world.flow

# Compile via MLIR and run (requires LLVM/MLIR tools)
./flow mlir-run examples/basics/hello_world.flow
```

### VS Code Extension

Install from `third_party/integrations/vscode/flow-language/flow-language-0.1.0.vsix`

---

## Known Issues & Security Status

A comprehensive audit (Feb 2026) identified 98 issues. **All 98 have been resolved** (100%) as of Feb 10, 2026.
The Feb 10, 2026 follow-up audit found 3 CI hygiene gaps (pinning, lint depth, security scanning); see the
latest audit report.

| Category | Status | Notes |
|----------|--------|-------|
| Testing | 5/5 resolved | All test infrastructure issues fixed |
| CLI | 5/5 resolved | Shell injection, temp dirs, validation fixed |
| Stdlib | 13/13 resolved | POSIX constants, memory pools, alignment fixed |
| Compiler | 58/58 resolved | MLIR, module resolver, monomorphize stabilized |
| Runtime | 6/6 resolved | Command injection, null deref, resource leaks fixed |
| CI | 6/6 resolved | Pipeline hardened and validated |

See [docs/project/AUDIT_2026-02-10.md](docs/project/AUDIT_2026-02-10.md) for the latest findings,
[docs/NEXT.md](docs/NEXT.md) for the prioritized roadmap, and [CHANGELOG](docs/project/CHANGELOG.md)
for details on what was fixed.

---

## Documentation

- **[Getting Started](docs/getting-started.md)** - Installation, first program
- **[Language Spec](docs/LANGUAGE_SPEC.md)** - Complete reference
- **[Concurrency vs Go](docs/language/concurrency-vs-go.md)** - Channels, fibers, OpenMP, netpoll
- **[Replacing Go](docs/language/replace-go.md)** - Scorecard for Go-shaped workloads
- **[Async via Effects](docs/language/async-effects.md)** - FiberAsync / ThreadedAsync / NetpollAsyncIO
- **[Package Registry](docs/project/package-registry.md)** - `search` / `add` / `publish`
- **[Examples](examples/README.md)** - All example programs
- **[Examples Compile Status](examples/STATUS.md)** - Verified compile status (986/1193)
- **[Effects Showcase](docs/effects-showcase.md)** - Algebraic effects walkthrough with honest limitations
- **[What's Next](docs/NEXT.md)** - Prioritized roadmap
- **[Changelog](docs/project/CHANGELOG.md)** - Version history and audit fixes
- **[Contributing](docs/project/CONTRIBUTING.md)** - How to contribute, security policy

---

## License

MIT License - see [LICENSE](LICENSE)

---

<p align="center">
  <img src="docs/assets/flow-mascot.png" alt="Flowy" width="80">
  <br>
  <em>Made with 💜 by humans and AI</em>
</p>
