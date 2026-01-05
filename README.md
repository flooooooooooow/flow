# FLOW Programming Language

A statically typed, explicit syntax language designed for MLIR/LLVM IR transpilation. FLOW demonstrates classic programming patterns (OOP, composition, algorithms) with a clean, modern toolchain.

## ✨ Features

- **Statically Typed**: Explicit type annotations (`i32`, `bool`, custom structs)
- **OOP Support**: Structs with field access and method-like functions
- **Composition**: Nested structs and "has-a" relationships
- **Classic Algorithms**: Fibonacci, factorial, GCD, sorting, searching
- **Modern Toolchain**: Python package with C backend for reliable execution
- **MLIR Ready**: Generates MLIR (experimental) and C code (production)

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- clang (for C compilation)

### Installation

```bash
git clone https://github.com/yourusername/flow-lang.git
cd flow-lang
```

### Running Your First Program

```bash
# List available examples
./flow examples

# Run a program (compiles via C backend)
./flow run examples/hello_world.flow

# Compile only
./flow compile examples/fibonacci.flow

# Generate MLIR (requires MLIR tools)
./flow mlir examples/loops.flow

# Run all tests
./flow test
```

## 📁 Project Structure

```
flow-lang/
├── flow              # CLI tool (dev runner)
├── pyproject.toml    # Python packaging metadata
├── src/flow/         # Compiler implementation (Python package)
│   ├── transpiler.py
│   ├── parser.py
│   ├── c_generator.py
│   └── mlir_generator.py
├── examples/         # Standard programs (C++-style examples)
├── tests/            # Compiler/language demos
├── build/            # Build output
├── docs/             # Documentation
└── tools/            # Misc tools / experiments
```

## 🏃 Running Programs

Right now `flow run` uses a **fast, reliable execution path**:

- FLOW → C via the compiler backend (`--c`)
- C → native executable via `clang`

Programs "return" values via their process exit code (until we add real I/O).

## 💻 Language Features

### Basic Syntax

```flow
function add(a: i32, b: i32) -> i32 {
    return a + b
}

- **Unbounded Recursion**: Can compute any computable function
- **Unbounded Loops**: While loops can run indefinitely
- **Conditional Branching**: Full if/else logic
- **State Manipulation**: Arbitrary variable updates

## 🔧 Architecture

### Compilation Pipeline

```
FLOW Source → Parser → AST → MLIR Generator → MLIR → LLVM IR → Native Code
```

### Components

1. **Parser** (`parser.py`): Recursive descent parser with tokenization
2. **MLIR Generator** (`mlir_generator.py`): AST to MLIR conversion
3. **Transpiler** (`transpiler.py`): Main compilation pipeline
4. **CLI Tool** (`flow`): User-friendly command interface

## 📖 Examples

### Hello World

```flow
function main() -> i32 {
    return 42
}
```

### Fibonacci

```flow
function fibonacci(n: i32) -> i32 {
    if n <= 1 {
        return n
    } else {
        return fibonacci(n - 1) + fibonacci(n - 2)
    }
}

function main() -> i32 {
    return fibonacci(10)
}
```

### Loops and Math

```flow
function sum_range(start: i32, end: i32) -> i32 {
    let sum: i32 = 0
    let i: i32 = start
    
    while i <= end {
        sum = sum + i
        i = i + 1
    }
    
    return sum
}

function factorial(n: i32) -> i32 {
    let result: i32 = 1
    let i: i32 = 2
    
    while i <= n {
        result = result * i
        i = i + 1
    }
    
    return result
}
```

## 🧪 Testing

```bash
# Run all tests
./flow test

# Test specific program
./flow run examples/fibonacci.flow

# Check MLIR generation
./flow mlir examples/loops.flow
```

## 🛠️ Development

### Building from Source

```bash
# Setup environment
export PATH="/opt/homebrew/opt/llvm/bin:$PATH"

# Test compilation
python3 transpiler.py examples/hello_world.flow

# Generate MLIR
python3 transpiler.py examples/fibonacci.flow -o test.mlir

# Convert to LLVM IR
mlir-opt test.mlir --convert-func-to-llvm --convert-arith-to-llvm | mlir-translate --mlir-to-llvmir

# Compile to native
llc input.ll -filetype=obj -o output.o
clang output.o -o executable
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Submit a pull request

## 📚 Documentation

- [Language Design](docs/language_design.md) - Complete language specification
- [Turing Completeness Proof](docs/turing_proof.md) - Mathematical proof of completeness
- [MLIR Integration](docs/mlir_integration.md) - MLIR dialect mapping

## 🎯 Status

- ✅ **Core Language**: Parser, basic types, control flow
- ✅ **MLIR Generation**: Basic MLIR output
- ✅ **CLI Tool**: Complete development environment
- ✅ **Examples**: Working demonstration programs
- 🔄 **Advanced MLIR**: Full dialect support
- 🔄 **LLVMIR Backend**: Complete LLVM integration
- 🔄 **Standard Library**: I/O, collections, algorithms
- 🔄 **Optimization**: Performance tuning passes

## 🚀 Why FLOW?

### For LLMs
- **Predictable syntax** makes it easy to generate correct code
- **Explicit typing** eliminates inference errors
- **Regular grammar** reduces ambiguity
- **Minimal context** simplifies generation

### For Humans  
- **Readable syntax** that's easy to understand
- **Explicit control flow** for clear logic
- **Familiar concepts** from other languages
- **Good error messages** for debugging

### For Performance
- **Zero-cost abstractions** - no runtime overhead
- **Direct MLIR mapping** - optimal code generation
- **Explicit parallelism** - easy SIMD/vectorization
- **Memory control** - manual allocation for performance

FLOW achieves the ideal balance: **simple enough for LLMs to generate correctly, powerful enough for humans to write efficiently, and fast enough for production use**.

## 📄 License

MIT License - see LICENSE file for details.
