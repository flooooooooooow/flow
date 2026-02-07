# Flow Programming Language

[![CI](https://github.com/abhishekshivakumar/transpile/actions/workflows/ci.yml/badge.svg)](https://github.com/abhishekshivakumar/transpile/actions/workflows/ci.yml)

<img src="docs/assets/flow-mascot.png" alt="Flowy the Hedgehog" width="180" align="right">

A statically-typed, compiled language with **algebraic effects**, **automatic differentiation**, and **native graphics**.

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
| Flow source files | 189 files, 26k lines |
| Python compiler | 21 files, 12k lines |
| Standard library | 34 modules, 5k lines |
| Test files | 85 tests |
| Examples | 62 programs |

---

## Quick Start

```bash
git clone https://github.com/flow-lang/flow.git
cd flow
./flow run examples/basics/hello_world.flow
```

**Requirements:** Python 3.8+, Clang or GCC

---

## Directory Structure

```
flow/
│
├── flow                    # CLI entry point (bash script)
├── flow-lsp                # Language Server Protocol launcher
├── README.md               # This file
├── ROADMAP.md              # Development roadmap
├── LICENSE                 # MIT License
├── Makefile                # Build automation
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
│   └── playground/         # Web playground
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
├── wasm/                   # WEBASSEMBLY (experimental)
│   └── ...
│
└── site/                   # MKDOCS WEBSITE
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

### Automatic Differentiation

```flow
# Forward-mode autodiff built into the language
# Used for neural networks, optimization, physics
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
./flow python <file>        # Generate Python wheel
./flow test                 # Run test suite
./flow fmt <file>           # Format code
./flow repl                 # Interactive mode
./flow jit <file>           # JIT compile (requires LLVM)
./flow lsp                  # Start language server
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

## Highlighted Examples

### Games (with Native Graphics)

```bash
# Tetris - fully playable!
./flow compile examples/games/tetris_gfx.flow
clang -O2 build/tetris_gfx.c runtime/gfx_macos.m \
    -framework Cocoa -framework CoreGraphics -framework QuartzCore \
    -o build/tetris && ./build/tetris

# 2048 puzzle
./flow compile examples/games/2048_gfx.flow
# ... same clang command
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
| Built-in Autodiff | ✅ | ❌ | ❌ | ✅ | ✅ |
| C Backend (portable) | ✅ | ❌ | ❌ | ❌ | ❌ |
| Native Graphics | ✅ | ❌ | ❌ | ❌ | ❌ |
| No LLVM Required | ✅ | ❌ | ✅ | ❌ | ❌ |

---

## Development

```bash
# Run tests
./flow test

# Format code
./flow fmt examples/basics/hello_world.flow

# Start LSP for IDE support
./flow lsp
```

### VS Code Extension

Install from `third_party/integrations/vscode/flow-language/flow-language-0.1.0.vsix`

---

## Documentation

- **[Getting Started](docs/getting-started.md)** - Installation, first program
- **[Language Spec](docs/LANGUAGE_SPEC.md)** - Complete reference
- **[Examples](examples/README.md)** - All example programs
- **[Roadmap](ROADMAP.md)** - What's next
- **[Contributing](CONTRIBUTING.md)** - Human-AI collaboration guidelines

---

## License

MIT License - see [LICENSE](LICENSE)

---

<p align="center">
  <img src="docs/assets/flow-mascot.png" alt="Flowy" width="80">
  <br>
  <em>Made with 💜 by humans and AI</em>
</p>
