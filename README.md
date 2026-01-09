# FLOW Programming Language

> A language designed by human intuition, implemented by machine precision.

**Version**: 0.3.0 | **Tests**: 166 passing | **Status**: Feature Complete 🎉

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Motivation](#motivation)
   - [The Problem with AI-Generated Code](#the-problem-with-ai-generated-code)
   - [The Solution: Linguistic Grounding](#the-solution-linguistic-grounding)
   - [Why Not Just Use Existing Languages?](#why-not-just-use-existing-languages)
3. [Design Philosophy](#design-philosophy)
   - [What FLOW Is Trying To Be](#what-flow-is-trying-to-be)
   - [What FLOW Is NOT](#what-flow-is-not)
   - [The Epistemic Contract](#the-epistemic-contract)
4. [Language Features](#language-features)
   - [Core Syntax](#core-syntax)
   - [Type System](#type-system)
   - [Effect System](#effect-system)
   - [Automatic Differentiation](#automatic-differentiation)
   - [Module System](#module-system)
5. [Compiler Architecture](#compiler-architecture)
   - [Pipeline Overview](#pipeline-overview)
   - [Backends](#backends)
   - [Tooling](#tooling)
6. [The Standardization Challenge](#the-standardization-challenge)
   - [How Languages Fragment](#how-languages-fragment)
   - [How FLOW Resists Fragmentation](#how-flow-resists-fragmentation)
7. [Current Status](#current-status)
   - [What's Implemented](#whats-implemented)
   - [What's In Progress](#whats-in-progress)
   - [What's Planned](#whats-planned)
8. [Project Structure](#project-structure)
9. [CLI Reference](#cli-reference)
10. [Examples](#examples)
11. [The Human-AI Collaboration Model](#the-human-ai-collaboration-model)
12. [For the Skeptics](#for-the-skeptics)
13. [Contributing](#contributing)
14. [License](#license)

---

## Quick Start

**🎮 [Try FLOW in the Web Playground](docs/playground/index.html)** — No installation required!

```bash
# Clone and run
git clone https://github.com/yourusername/flow-lang.git
cd flow-lang

# Run a program
./flow run examples/basics/hello_world.flow

# Start the REPL
./flow repl

# JIT compile and run (fastest)
./flow jit examples/basics/fibonacci.flow

# Generate MLIR and run via LLVM
./flow mlir-run examples/basics/factorial.flow

# Generate GPU shaders
./flow gpu examples/gpu/vector_add_gpu.flow

# Initialize a new project
./flow init my-project

# Run all tests
./flow test

# Format code
./flow fmt myfile.flow
```

**Hello World**:

```flow
function main() -> i32 {
    printf("Hello, FLOW!\n")
    return 0
}
```

**Fibonacci with Generics**:

```flow
function fibonacci(n: i32) -> i32 {
    if n <= 1 {
        return n
    }
    return fibonacci(n - 1) + fibonacci(n - 2)
}
```

**GPU Compute Shader**:

```flow
@gpu
function vector_add(a: array<f32>, b: array<f32>, out: array<f32>, n: i32) {
    let i = gpu_thread_id()
    if i < n {
        out[i] = a[i] + b[i]
    }
}
```

---

## Motivation

### The Problem with AI-Generated Code

Programming languages are **linguistic artifacts**. Like natural languages, they encode ways of thinking, constrain what's expressible, and drift semantically over time. 

Most languages emerge from one of three paths:

| Path | Examples | Strength | Weakness |
|------|----------|----------|----------|
| **Single vision** | Rust, Python, Go | Coherent design | Bottlenecked by one person |
| **Committee design** | C++, JavaScript, SQL | Comprehensive | Inconsistent, political |
| **Accidental evolution** | PHP, Perl, Bash | Pragmatic | Chaotic, legacy debt |

FLOW experiments with a **fourth path**: AI implementation with human grounding.

**The core problem**: LLMs generate syntactically correct code but suffer from:

- **Semantic inconsistency** — The same concept gets different names across files
- **Architectural incoherence** — Local decisions don't compose globally
- **Conceptual drift** — Abstractions shift meaning as context changes

Without a grounding force, AI-generated systems become internally inconsistent. Each generation makes locally reasonable choices that globally diverge. We call this **semantic drift**.

### The Solution: Linguistic Grounding

FLOW inverts the typical AI-assisted workflow:

```
Traditional:     Human designs → Human implements → Human documents
AI-assisted:     Human designs → AI implements → AI documents (drift accumulates)
FLOW:            Human grounds → AI implements → Human re-grounds (drift corrected)
```

**The human role** isn't to write code — it's to:
- **Name things consistently** (semantic anchoring)
- **Catch conceptual drift** before it compounds  
- **Maintain the linguistic contract** between syntax and meaning
- **Decide what matters** — features, priorities, tradeoffs

**The AI role** is to:
- **Handle implementation complexity** (parsers, code generators, edge cases)
- **Generate exhaustive test coverage**
- **Explore design variations** faster than humans can
- **Maintain consistency** once patterns are established

### Why Not Just Use Existing Languages?

**Why not Rust?** Rust's ownership model is brilliant for memory safety but adds cognitive overhead that obscures the code's *intent*. FLOW prioritizes readability over provable safety.

**Why not Python?** Python is dynamically typed, interpreted, and has no explicit effect tracking. FLOW is statically typed, compiled, and makes side effects visible.

**Why not Zig?** Zig is excellent but focuses on replacing C with minimal runtime. FLOW focuses on making effects and gradients first-class citizens.

**Why not JAX/PyTorch?** These are Python libraries, not languages. FLOW embeds autodiff into the language itself, making gradients as natural as integers.

**The honest answer**: FLOW exists because the human behind it wanted to explore what a language designed *with* AI looks like, not just what a language designed *for* AI looks like.

---

## Design Philosophy

### What FLOW Is Trying To Be

#### 1. Maximally Explicit

FLOW rejects implicit behavior. Every operation should be readable by someone who's never seen the language:

```flow
# Clear: you know exactly what this does
function add(a: i32, b: i32) -> i32 {
    return a + b
}

# Explicit types: no inference magic
let x: i32 = 42
let y: f32 = 3.14

# Explicit effects: side effects are declared, not hidden
effect Log {
    emit(message: string) -> void
}
```

**Why this matters**: Implicit behavior is where semantic drift hides. If the human grounding force can't immediately see what code does, they can't catch drift. Explicit code is auditable code.

#### 2. Effects-First

Most languages treat side effects as invisible — I/O, state mutation, exceptions happen anywhere. FLOW makes them explicit and scoped:

```flow
# Declare what effects exist
effect Database {
    query(sql: string) -> array<Row>
    insert(table: string, data: Row) -> void
}

# Implement the effect concretely
capability PostgresDB {
    query(sql: string) -> array<Row> {
        # actual postgres calls
    }
    insert(table: string, data: Row) -> void {
        # actual postgres calls
    }
}

# Scope where effects can happen
function main() -> i32 {
    handle Database with PostgresDB {
        let users: array<Row> = Database.query("SELECT * FROM users")
        process_users(users)  # This function CANNOT call Database
    }
    return 0
}
```

**Why this matters**: "What does this function actually do?" is the most important question in programming. In FLOW, the answer is in the type signature. Functions that perform effects must declare them. Functions without effects are pure.

#### 3. Gradients as First-Class Citizens

Neural networks are the primary consumer of programming languages in 2025+. FLOW treats automatic differentiation as a core feature:

```flow
import "stdlib/autodiff.flow"

# Dual numbers track value AND derivative simultaneously
function compute_gradient() -> void {
    let x: Dual = Dual { val: 2.0, grad: 1.0 }  # d/dx at x=2
    let y: Dual = dual_exp(dual_sq(x))          # e^(x²)
    
    printf("f(2) = %f\n", get_val(y))    # e^4 ≈ 54.6
    printf("f'(2) = %f\n", get_grad(y))  # 4e^4 ≈ 218.4
}
```

**Why this matters**: When gradients are a library feature, they fight the language. When they're a language feature, everything composes naturally. FLOW's autodiff works with the type system, not against it.

#### 4. Multi-Target Compilation

FLOW compiles to multiple backends from a single source:

| Target | Use Case | Status |
|--------|----------|--------|
| **C99** | Portable, debuggable, runs anywhere | ✅ Stable |
| **MLIR** | Optimizable, GPU/TPU targeting | ⚠️ Experimental |
| **WebAssembly** | Browser deployment | ⚠️ Via Emscripten |

**Why this matters**: The future is heterogeneous. Code must run on CPUs, GPUs, browsers, edge devices. One language, many targets, same semantics.

### What FLOW Is NOT

| NOT | WHY |
|-----|-----|
| **Production-ready** | Active experiment. Breaking changes happen. Compiler is Python for iteration speed. |
| **A Rust replacement** | Rust has decades of optimization and a massive ecosystem. FLOW explores different tradeoffs. |
| **A Python replacement** | FLOW is statically typed, compiled, no runtime. Different domain. |
| **An AI code generator** | FLOW isn't for generating code in other languages. It's a language designed with AI in the loop. |
| **Complete** | Missing generics, full pattern matching, package manager. See [What's Planned](#whats-planned). |

### The Epistemic Contract

When you read FLOW code, you can trust:

| Claim | Guarantee | Mechanism |
|-------|-----------|-----------|
| **Types are enforced** | Type annotations are verified | `type_checker.py` |
| **Effects are visible** | Side-effecting functions declare effects | Effect system |
| **Imports are explicit** | No global state, no implicit deps | Module resolver |
| **Behavior is local** | Function behavior = inputs + declared effects | Pure by default |
| **Syntax is stable** | `grammar.ebnf` is the contract | Parser validation |

This is the **epistemic contract**: what you see is what you get. The language actively resists hidden complexity.

---

## Language Features

### Core Syntax

```flow
# Comments start with #
// Or C-style

# Functions
function factorial(n: i32) -> i32 {
    if n <= 1 {
        return 1
    }
    return n * factorial(n - 1)
}

# Variables (immutable by default)
let x: i32 = 42
let pi: f32 = 3.14159

# Control flow
if condition {
    # then
} elif other_condition {
    # else if
} else {
    # else
}

while condition {
    # loop
}

for i in 0 to 10 {
    # range loop
}

for i in 0 to 100 step 5 {
    # with step
}
```

### Type System

| Type | Description | Example |
|------|-------------|---------|
| `i8`, `i16`, `i32`, `i64`, `i128` | Signed integers | `let x: i32 = -42` |
| `u8`, `u16`, `u32`, `u64`, `u128` | Unsigned integers | `let x: u8 = 255` |
| `f32`, `f64` | Floating point | `let x: f64 = 3.14159` |
| `bool` | Boolean | `let x: bool = true` |
| `string` | String | `let x: string = "hello"` |
| `void` | No return value | `function log(msg: string) -> void` |
| `array<T>` | Dynamic array | `let x: array<i32> = [1, 2, 3]` |
| `array<T, N>` | Fixed-size array | `let x: array<i32, 3> = [1, 2, 3]` |
| `ptr<T>` | Pointer | `let x: ptr<i32> = alloc(4)` |
| `struct` | User-defined type | See below |

**Structs**:

```flow
struct Point {
    x: f32
    y: f32
}

struct Color {
    r: u8
    g: u8
    b: u8
    a: u8
}

function distance(a: Point, b: Point) -> f32 {
    let dx: f32 = b.x - a.x
    let dy: f32 = b.y - a.y
    return sqrt(dx * dx + dy * dy)
}
```

### Effect System

Effects are FLOW's mechanism for explicit side-effect tracking:

```flow
# 1. Declare an effect (abstract interface)
effect Logger {
    log(level: string, message: string) -> void
    get_log_count() -> i32
}

# 2. Implement the effect (concrete capability)
capability ConsoleLogger {
    log(level: string, message: string) -> void {
        printf("[%s] %s\n", level, message)
    }
    get_log_count() -> i32 {
        return 0  # Simplified
    }
}

capability FileLogger {
    log(level: string, message: string) -> void {
        # Write to file instead
    }
    get_log_count() -> i32 {
        return 0
    }
}

# 3. Use the effect (scoped by handler)
function do_work() -> void {
    Logger.log("INFO", "Starting work")
    # ... work ...
    Logger.log("INFO", "Done")
}

function main() -> i32 {
    # Console logging
    handle Logger with ConsoleLogger {
        do_work()
    }
    
    # Same code, different effect implementation
    handle Logger with FileLogger {
        do_work()
    }
    
    return 0
}
```

**Key properties**:
- Functions that use effects must be called within a handler
- Effects are resolved at compile time (no runtime overhead)
- Different handlers can provide different implementations
- Effect scope is lexical and visible

### Automatic Differentiation

FLOW supports both forward and reverse mode autodiff:

**Forward Mode (Dual Numbers)**:

```flow
import "stdlib/autodiff.flow"

# Dual numbers carry value and derivative
struct Dual {
    val: f32   # f(x)
    grad: f32  # f'(x)
}

# Seed with d/dx = 1 at the input you care about
let x: Dual = Dual { val: 2.0, grad: 1.0 }

# Chain rule applied automatically through operations
let y: Dual = dual_sin(dual_mul(x, x))  # sin(x²)
# y.grad contains d/dx[sin(x²)] = 2x·cos(x²)
```

**Reverse Mode (Manual Backprop)**:

```flow
import "stdlib/autodiff_reverse.flow"
import "stdlib/nn.flow"

# Neural network with backpropagation
let net: Net2x2x1 = Net2x2x1 { ... }
let grads: Grads2x2x1 = net2x2x1_grads_xor(net, 0.0, 1.0, 1.0)
let new_net: Net2x2x1 = net2x2x1_step(net, grads, 0.1)
```

**Gradient Codegen**:

```bash
# Generate gradient code automatically
python3 tools/flow_grad_flow.py lib/stdlib/nn_xor_loss_clean.flow
# Outputs: lib/stdlib/nn_xor_loss_clean_grad.flow
```

### Module System

```flow
# Import a module
import "stdlib/math.flow"
import "stdlib/autodiff.flow"
import "../utils/helpers.flow"

# Export functions/structs
export function public_api(x: i32) -> i32 {
    return internal_helper(x) * 2
}

function internal_helper(x: i32) -> i32 {
    return x + 1
}

export struct PublicType {
    value: i32
}
```

**Features**:
- Relative and absolute paths
- `lib/stdlib/` for standard library
- Circular import detection with warnings
- Symbol visibility (`export` keyword)

---

## Compiler Architecture

### Pipeline Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Source Code (.flow)                      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Lexer (parser.py)                         │
│  Tokenizes source into NUMBER, IDENTIFIER, KEYWORD, etc.    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│               Recursive Descent Parser (parser.py)           │
│  Builds AST: FunctionDecl, StructDecl, IfStatement, etc.    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│               Module Resolver (module_resolver.py)           │
│  Handles imports, builds dependency graph, detects cycles   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                Type Checker (type_checker.py)                │
│  Symbol tables, scope analysis, type verification           │
└─────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┴───────────────┐
              ▼                               ▼
┌──────────────────────────┐    ┌──────────────────────────────┐
│   C Generator            │    │    MLIR Generator            │
│   (c_generator.py)       │    │    (mlir_generator.py)       │
│   900 lines              │    │    500 lines                 │
└──────────────────────────┘    └──────────────────────────────┘
              │                               │
              ▼                               ▼
┌──────────────────────────┐    ┌──────────────────────────────┐
│   C99 Source Code        │    │   MLIR Dialects              │
│   (portable)             │    │   (func, arith, scf)         │
└──────────────────────────┘    └──────────────────────────────┘
              │                               │
              ▼                               ▼
┌──────────────────────────┐    ┌──────────────────────────────┐
│   clang / emcc           │    │   mlir-opt → llc             │
└──────────────────────────┘    └──────────────────────────────┘
              │                               │
              ▼                               ▼
┌──────────────────────────┐    ┌──────────────────────────────┐
│   Native / WASM          │    │   Native (experimental)      │
└──────────────────────────┘    └──────────────────────────────┘
```

### Backends

| Backend | File | Output | Status |
|---------|------|--------|--------|
| **C** | `c_generator.py` | C99 source | ✅ Stable |
| **MLIR** | `mlir_generator.py` | MLIR dialects | ⚠️ Experimental |
| **WASM** | `wasm/flow_to_wasm.py` | WebAssembly | ⚠️ Via Emscripten |

### Tooling

| Tool | File | Purpose |
|------|------|---------|
| **Parser** | `parser.py` | Lexer + Parser + AST (1300 lines) |
| **Type Checker** | `type_checker.py` | Semantic analysis (525 lines) |
| **Formatter** | `formatter.py` | Code formatting (114 lines) |
| **Test Runner** | `test_runner.py` | Native test framework |
| **LSP Server** | `lsp_server.py` | Editor integration (minimal) |
| **Gradient Codegen** | `tools/flow_grad_flow.py` | Auto-generate backprop |

---

## The Standardization Challenge

### How Languages Fragment

Languages die from **semantic fragmentation**:

1. **Early adoption**: Core team agrees on meaning
2. **Growth**: New contributors bring different mental models
3. **Dialects emerge**: "Pythonic", "Modern C++", "Idiomatic Go"
4. **Fragmentation**: Same syntax, different semantics
5. **Stagnation or fork**: Community splits or progress halts

**Examples**:
- JavaScript: `this` means 5 different things depending on context
- Python: "Pythonic" is undefined and contested
- C++: Template metaprogramming vs "clean" C++ are different languages
- Lisp: Scheme, Common Lisp, Clojure are barely compatible

### How FLOW Resists Fragmentation

| Mechanism | File | Purpose |
|-----------|------|---------|
| **Roadmap** | `ROADMAP.md` | What we're building next, and why |
| **Language Spec** | `docs/LANGUAGE_SPEC.md` | Single source of truth for all features |
| **Implementation Map** | `docs/IMPLEMENTATION_MAP.md` | Every concept → exact code location |
| **Formal Grammar** | `docs/grammar.ebnf` | Syntax contract (291 lines) |
| **Exhaustive Tests** | `tests/` + `examples/` | 152 tests verify full surface |
| **Human Grounding** | This README | Semantic arbiter catches drift |

**The key insight**: Fragmentation happens when meaning drifts without anyone noticing. FLOW's human-in-the-loop catches drift at the source, before it compounds into dialects.

---

## Current Status

### What's Implemented

| Component | Lines | Description |
|-----------|-------|-------------|
| **Parser** | 1,300 | Lexer, recursive descent parser, full AST |
| **Type Checker** | 525 | Symbol tables, scopes, type verification |
| **C Generator** | 900 | Complete C99 output with effects |
| **MLIR Generator** | 500 | Experimental MLIR output |
| **Formatter** | 114 | Basic code formatting |
| **Module Resolver** | 300 | Imports, exports, cycle detection |
| **Standard Library** | 600 | Math, autodiff, neural nets |

**Feature Status**:

| Feature | Status | Notes |
|---------|--------|-------|
| Primitive types | ✅ | i8-i128, u8-u128, f32, f64, bool, string |
| Structs | ✅ | User-defined types with fields |
| Functions | ✅ | Parameters, returns, recursion |
| Control flow | ✅ | if/elif/else, while, for, match |
| Arrays | ✅ | Dynamic and fixed-size |
| Pointers | ✅ | ptr<T> with explicit management |
| Effects | ✅ | Declare, implement, handle |
| Modules | ✅ | Import/export with cycle detection |
| Forward-mode AD | ✅ | Dual numbers |
| Reverse-mode AD | ✅ | Manual + codegen |
| C backend | ✅ | Portable C99 |
| Test framework | ✅ | `test` keyword, 152 passing |

### What's In Progress

| Component | Status | Blocker |
|-----------|--------|---------|
| MLIR backend | ⚠️ | Optimization passes incomplete |
| GPU/Metal | ⚠️ | Runtime exists, codegen incomplete |
| LSP | ⚠️ | Only syntax highlighting |
| WASM | ⚠️ | Works via Emscripten, not native |

### What's Planned

| Feature | Priority | Estimated Effort |
|---------|----------|------------------|
| Generics (`<T>`) | High | 1-2 weeks |
| Strict type enforcement | High | 3-5 days |
| Full pattern matching | Medium | 1 week |
| Trait/interface system | Medium | 1-2 weeks |
| Closures (full) | Medium | 1 week |
| Package manager | Low | 2-3 weeks |
| REPL | Low | 1 week |
| Debugger integration | Low | 2+ weeks |

---

## Project Structure

```
flow/
├── flow                      # CLI entry point (bash, 350 lines)
├── flow-lsp                  # LSP launcher (bash)
├── ROADMAP.md                # What we're building next
├── Makefile                  # Build automation
│
├── src/flow/                 # Compiler implementation (Python)
│   ├── __init__.py
│   ├── parser.py             # Lexer + Parser + AST (1300 lines)
│   ├── type_checker.py       # Semantic analysis (525 lines)
│   ├── c_generator.py        # C code generation (900 lines)
│   ├── mlir_generator.py     # MLIR generation (500 lines)
│   ├── formatter.py          # Code formatting (114 lines)
│   ├── module_resolver.py    # Multi-file compilation (300 lines)
│   ├── transpiler.py         # CLI logic
│   ├── test_runner.py        # Test framework
│   ├── lsp_server.py         # Language Server Protocol
│   ├── gpu_integration.py    # GPU abstraction layer
│   ├── metal_runtime.py      # Apple Metal backend
│   ├── mlir_jit.py           # JIT compilation
│   └── mlir_optimizer.py     # MLIR optimization passes
│
├── lib/stdlib/               # Standard library (FLOW)
│   ├── autodiff.flow         # Forward-mode dual numbers
│   ├── autodiff_reverse.flow # Reverse-mode helpers
│   ├── nn.flow               # Neural network layers (2x2x1, 2x4x1, 2x8x1)
│   ├── math.flow             # Math functions
│   └── memory.flow           # Memory utilities
│
├── examples/                 # 86 example programs
│   ├── hello_world.flow
│   ├── fibonacci.flow
│   ├── neural_network.flow
│   ├── autodiff_demo.flow
│   └── ...
│
├── tests/                    # 66 test files
│   ├── core/                 # Core language tests
│   ├── stdlib/               # Standard library tests
│   └── *.py                  # Python test infrastructure
│
├── docs/                     # Documentation
│   ├── LANGUAGE_SPEC.md      # Authoritative specification
│   ├── IMPLEMENTATION_MAP.md # Code location mapping
│   ├── grammar.ebnf          # Formal grammar (291 lines)
│   ├── getting-started.md
│   ├── language/             # Language feature docs
│   ├── library/              # Standard library docs
│   └── tutorials/            # Learning guides
│
├── tools/                    # Development tools
│   ├── flow_grad_flow.py     # Gradient codegen (FLOW output)
│   ├── flow_grad_c.py        # Gradient codegen (C output)
│   ├── flow_jit_pipeline.py  # JIT compilation
│   └── srir_viewer.py        # IR visualization
│
├── wasm/                     # WebAssembly tooling
│   ├── flow_to_wasm.py
│   ├── wasm_build_system.py
│   └── wasm_demo/
│
├── editors/                  # Editor support
│   └── vscode/flow-language/ # VS Code extension
│
└── build/                    # Compilation output
```

---

## CLI Reference

```bash
# Compile and run
./flow run <file.flow>

# Compile only (output: build/<name>)
./flow compile <file.flow>

# Format source code
./flow fmt <file.flow>

# Run all tests (152 tests)
./flow test

# Generate MLIR
./flow mlir <file.flow>

# Advanced transpiler flags
./flow transpile <file.flow> --c --o output.c
./flow transpile <file.flow> --mlir --optimize

# List example programs
./flow examples

# Show help
./flow help
```

---

## Examples

### Fibonacci

```flow
function fibonacci(n: i32) -> i32 {
    if n <= 1 {
        return n
    }
    return fibonacci(n - 1) + fibonacci(n - 2)
}

function main() -> i32 {
    let result: i32 = fibonacci(10)
    printf("fib(10) = %d\n", result)
    return 0
}
```

### Effect System

```flow
effect Log {
    emit(message: string) -> void
}

capability ConsoleLogger {
    emit(message: string) -> void {
        printf("[LOG] %s\n", message)
    }
}

function main() -> i32 {
    handle Log with ConsoleLogger {
        Log.emit("Hello from effects!")
    }
    return 0
}
```

### Neural Network (XOR)

```flow
import "stdlib/nn.flow"

function main() -> i32 {
    # Initialize network
    let net: Net2x2x1 = Net2x2x1 {
        w00: 0.5, w01: 0.5, w10: 0.5, w11: 0.5,
        b0: 0.0, b1: 0.0, v0: 0.5, v1: 0.5, c: 0.0
    }
    
    # Train on XOR
    for epoch in 0 to 1000 {
        let grads: Grads2x2x1 = net2x2x1_grads_xor(net, 0.0, 0.0, 0.0)
        net = net2x2x1_step(net, grads, 0.1)
    }
    
    # Test
    let p00: f32 = net2x2x1_predict(net, 0.0, 0.0)  # → 0
    let p01: f32 = net2x2x1_predict(net, 0.0, 1.0)  # → 1
    let p10: f32 = net2x2x1_predict(net, 1.0, 0.0)  # → 1
    let p11: f32 = net2x2x1_predict(net, 1.0, 1.0)  # → 0
    
    return 0
}
```

---

## The Human-AI Collaboration Model

This project exists because of a specific collaboration pattern:

### The Loop

```
┌─────────────────────────────────────────────────────────────┐
│                     Human Intent                             │
│  "I want effects to be explicit and traceable"              │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   AI Implementation                          │
│  Generates parser rules, AST nodes, code generator,         │
│  tests, documentation                                        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   Human Verification                         │
│  "This doesn't match my mental model" or "This is right"    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    AI Refinement                             │
│  Fixes issues, maintains consistency with established        │
│  patterns, updates tests and docs                            │
└─────────────────────────────────────────────────────────────┘
                              │
                              └──────────────► (repeat)
```

### Division of Labor

| Task | Human | AI |
|------|-------|-----|
| "What should exist" | ✓ | |
| "How should it work" | ✓ | |
| Implementation | | ✓ |
| Edge cases | | ✓ |
| Test generation | | ✓ |
| Semantic consistency | ✓ | |
| Documentation | | ✓ (initial) |
| Documentation review | ✓ | |

### Why This Works

1. **AI speed + Human coherence**: AI implements 10x faster than humans but drifts. Human catches drift before it compounds.

2. **Exhaustive coverage**: AI generates tests humans wouldn't think of. Human ensures tests match intent.

3. **Rapid iteration**: Ideas can be prototyped in minutes, verified in seconds, refined continuously.

4. **Semantic anchoring**: Human's linguistic awareness prevents the "everything is slightly wrong" problem of pure AI generation.

---

## For the Skeptics

*This section addresses common criticisms directly. If you're excited about FLOW, skip ahead. If you think this is stupid, read on.*

### "AI-generated code is unreliable garbage"

**Valid concern.** Most AI-generated code *is* unreliable garbage. Here's why FLOW is different:

| Typical AI Code | FLOW |
|-----------------|------|
| Generated once, never verified | 152 tests verify every feature |
| No coherent architecture | Single human maintains semantic consistency |
| Drifts with each generation | Human re-grounds after each session |
| No specification | `LANGUAGE_SPEC.md` is authoritative |
| Works by accident | Works because it's tested |

**The honest truth**: About 30% of AI-generated code in this project was wrong on first try. The difference is that every piece was verified, tested, and corrected. The AI generates *candidates*; the human and test suite determine *correctness*.

### "You're just reinventing the wheel"

**Partially true.** FLOW doesn't do anything that *couldn't* be done in other languages:
- Effects? Haskell, Koka, Eff have them
- Autodiff? JAX, PyTorch, Enzyme have it
- Multi-backend? MLIR, Halide exist

**What's new** is the combination:
1. Effects + Autodiff + Multi-backend in one language
2. Designed *with* AI, not just *for* AI
3. Explicit exploration of human-AI collaboration patterns

If that's not interesting to you, fair enough. Use the existing tools.

### "This will never scale / get adoption"

**Probably true.** Most languages fail. FLOW likely will too, by typical metrics.

But "success" isn't the only goal:
- **Learning**: Building a compiler teaches you how languages work
- **Exploration**: What *does* human-AI collaboration look like?
- **Documentation**: This README documents patterns others can use
- **Personal utility**: Sometimes you build tools for yourself

If FLOW never gets a single external user, it will still have been worth building. The process *is* the product.

### "The compiler is written in Python lmao"

**Yes.** Here's why:

| Python | Systems Language |
|--------|-----------------|
| 3 weeks to working compiler | 3 months minimum |
| Easy to iterate | Compile times slow iteration |
| AI can generate/modify easily | AI struggles with Rust lifetimes |
| "Fast enough" for prototyping | Premature optimization |

**The plan**: If FLOW proves useful, rewrite in Rust/Zig. Until then, Python lets us iterate 10x faster. The compiler being slow doesn't make the *output* slow — FLOW compiles to C, which compiles to native code.

### "AI will make this obsolete in 6 months"

**Maybe.** If AI gets good enough to design coherent languages without human grounding, FLOW becomes obsolete. That would be great! We'd have solved a hard problem.

**More likely**: AI will get better at implementation while still needing human grounding for coherence. FLOW is an experiment in that specific collaboration pattern. Even if the *language* becomes obsolete, the *pattern* might remain useful.

### "This is just AI hype / vaporware"

**152 tests pass.** You can run them:

```bash
git clone https://github.com/yourusername/flow-lang.git
cd flow-lang
./flow test
```

The code exists. It compiles. It runs. It has:
- A complete parser (1300 lines)
- A type checker (525 lines)
- A C backend (900 lines)
- 86 example programs
- A neural network that learns XOR

"Vaporware" means promised but nonexistent. FLOW exists. Whether it's *good* is a separate question — but it's not vapor.

### "Nobody asked for this"

**Correct.** This wasn't built for a market. It was built because:

1. The human behind it wanted to understand compilers
2. AI made it possible to build one in weeks instead of months
3. The collaboration pattern itself was interesting to explore
4. Effects and autodiff deserved to be first-class somewhere

If you need a language backed by a company, with a roadmap, and a support contract — use Go, Rust, or TypeScript. They're excellent.

FLOW is for people who find the *process* interesting, not just the *product*.

### "You're not qualified to design a language"

**Probably true.** The human behind this isn't a PL researcher. They're someone who:
- Grew up multilingual (English/Tamil)
- Thinks about linguistic structure a lot
- Wanted to see what happens when AI implements a human's intuitions

**The counterpoint**: Most successful languages weren't designed by PL researchers either:
- Python: Guido was a physicist  
- Ruby: Matz was a programmer who liked Perl and Lisp
- JavaScript: Brendan Eich built it in 10 days
- Go: Rob Pike was a systems programmer, not a theorist

Sometimes "I want this to exist" is enough. The market (and time) will judge.

### "The effect system is just monads with extra steps"

**Yes and no.** Effects and monads solve similar problems (tracking computational context). Differences:

| Monads (Haskell-style) | Effects (FLOW-style) |
|------------------------|---------------------|
| Compositional via `>>=` | Compositional via handlers |
| Types get nested (`IO (Maybe (Either ...))`) | Flat effect sets |
| Library feature | Language feature |
| Requires understanding category theory (sort of) | Requires understanding scoping |

Both are valid. FLOW chose effects because they're more *visible* — you can see the handler scope syntactically. Whether that's better depends on what you value.

### "Autodiff should be a library, not a language feature"

**Reasonable position.** Most autodiff is implemented as libraries (JAX, PyTorch, TensorFlow).

**FLOW's bet**: When gradients are a *language* feature:
- The type system can track them
- Effects can scope differentiation
- No framework lock-in
- Smaller, more composable primitives

Maybe this is wrong. The experiment will tell us.

### "This documentation is too long"

**Fair.** Here's the short version:

1. FLOW is a language with explicit effects and built-in autodiff
2. It was built by a human-AI collaboration
3. 152 tests pass
4. It compiles to C
5. It's experimental
6. Use it if it interests you, ignore it if it doesn't

---

## Contributing

1. **Read the spec**: `docs/LANGUAGE_SPEC.md` is authoritative
2. **Check the map**: `docs/IMPLEMENTATION_MAP.md` shows where features live
3. **Run tests**: `./flow test` must pass
4. **Format code**: `./flow fmt` for FLOW files
5. **Maintain consistency**: New features should follow existing patterns

---

## License

MIT License - see [LICENSE](LICENSE)

---

## A Note on Names

"FLOW" captures multiple aspects of the language:

- **Data flow** — Values flow through pure functions
- **Control flow** — Explicit, visible, traceable branching
- **Effect flow** — Side effects are declared and scoped
- **Gradient flow** — Derivatives propagate through computation graphs

The name may change as the language evolves. What matters is that the *meaning* stays stable even if the *name* doesn't.

---

*Last updated: 2026-01-09*
