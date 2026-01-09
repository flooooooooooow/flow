# Getting Started with FLOW

Welcome to FLOW! This guide will get you from zero to productive in about 10 minutes.

## Table of Contents

1. [Installation](#installation)
2. [Hello World](#hello-world)
3. [The REPL](#the-repl)
4. [Creating a Project](#creating-a-project)
5. [Language Basics](#language-basics)
6. [Next Steps](#next-steps)

---

## Installation

### Requirements

- Python 3.8+
- GCC or Clang (for C backend)
- Optional: LLVM 15+ (for MLIR backend)

### Quick Setup

```bash
# Clone the repository
git clone https://github.com/flow-lang/flow.git
cd flow

# Verify installation
./flow --help

# Run tests to confirm everything works
./flow test
```

That's it! No pip install needed - FLOW runs directly from the repository.

---

## Hello World

Create a file called `hello.flow`:

```flow
function main() -> i32 {
    printf("Hello, FLOW!\n")
    return 0
}
```

Run it:

```bash
./flow run hello.flow
```

Output:
```
Hello, FLOW!
```

### What Just Happened?

1. **Parse**: FLOW parsed your code into an Abstract Syntax Tree (AST)
2. **Generate**: Converted the AST to portable C code
3. **Compile**: Used your system's C compiler (gcc/clang)
4. **Execute**: Ran the resulting binary

---

## The REPL

FLOW has an interactive mode for experimentation:

```bash
./flow repl
```

```
FLOW REPL v0.3.0
Type expressions, statements, or :help for commands

flow> 2 + 2
4
flow> let x = 10
x = 10
flow> x * 5
50
flow> function square(n: i32) -> i32 { return n * n }
Defined function square(n: i32) -> i32
flow> square(7)
49
flow> :quit
Goodbye!
```

### REPL Commands

| Command | Description |
|---------|-------------|
| `:help` | Show help |
| `:vars` | List defined variables |
| `:funcs` | List defined functions |
| `:clear` | Clear all definitions |
| `:quit` | Exit the REPL |

---

## Creating a Project

FLOW has a built-in package manager:

```bash
# Create a new project
./flow init my-app
cd my-app

# Project structure
my-app/
├── flow.toml        # Project configuration
├── src/
│   └── main.flow    # Entry point
└── .gitignore
```

### flow.toml

```toml
[package]
name = "my-app"
version = "0.1.0"
entry = "src/main.flow"

[dependencies]
# Add dependencies here
```

### Build and Run

```bash
./flow build    # Compile the project
./flow run src/main.flow  # Run the entry point
```

---

## Language Basics

### Variables

```flow
let x: i32 = 42          # Explicit type
let y = 3.14             # Type inferred as f64
let name: string = "FLOW"
let flag: bool = true
```

### Functions

```flow
function add(a: i32, b: i32) -> i32 {
    return a + b
}

function greet(name: string) -> void {
    printf("Hello, %s!\n", name)
}
```

### Control Flow

```flow
# If/else
if x > 0 {
    printf("positive\n")
} elif x < 0 {
    printf("negative\n")
} else {
    printf("zero\n")
}

# While loop
let i = 0
while i < 10 {
    printf("%d\n", i)
    i = i + 1
}

# For loop
for i in 0..10 {
    printf("%d\n", i)
}
```

### Structs

```flow
struct Point {
    x: f32,
    y: f32
}

function distance(p1: Point, p2: Point) -> f32 {
    let dx = p2.x - p1.x
    let dy = p2.y - p1.y
    return sqrt(dx * dx + dy * dy)
}

function main() -> i32 {
    let a = Point { x: 0.0, y: 0.0 }
    let b = Point { x: 3.0, y: 4.0 }
    printf("Distance: %f\n", distance(a, b))  # 5.0
    return 0
}
```

### Generics

```flow
struct Box<T> {
    value: T
}

function identity<T>(x: T) -> T {
    return x
}

function main() -> i32 {
    let int_box = Box<i32> { value: 42 }
    let float_val = identity<f32>(3.14)
    return 0
}
```

### Enums

```flow
enum Color {
    Red,
    Green,
    Blue,
    RGB(r: i32, g: i32, b: i32)
}

function main() -> i32 {
    let c = Color::Red
    let custom = Color::RGB(255, 128, 0)
    return 0
}
```

### Traits

```flow
trait Display {
    function show(self: Self) -> void
}

struct Person {
    name: string,
    age: i32
}

impl Display for Person {
    function show(self: Person) -> void {
        printf("%s, age %d\n", self.name, self.age)
    }
}
```

### Option and Result

```flow
import "stdlib/option.flow"
import "stdlib/result.flow"

function safe_divide(a: f64, b: f64) -> Result_f64_string {
    if b == 0.0 {
        return err_f64_string("division by zero")
    }
    return ok_f64_string(a / b)
}
```

---

## Execution Modes

FLOW supports multiple ways to run your code:

### 1. C Backend (Default)

```bash
./flow run program.flow
```

Compiles to C, then to native code. Most portable.

### 2. JIT Compilation

```bash
./flow jit program.flow
```

Uses MLIR → LLVM → native. Fastest for development.

### 3. MLIR Backend

```bash
./flow mlir-run program.flow
```

Full MLIR pipeline with optimizations.

### 4. GPU Shaders

```bash
./flow gpu program.flow
```

Generates Metal compute shaders for `@gpu` functions.

---

## Standard Library

Import modules from the standard library:

```flow
import "stdlib/math.flow"
import "stdlib/string.flow"
import "stdlib/collections.flow"
import "stdlib/net.flow"
import "stdlib/concurrent.flow"
import "stdlib/posix.flow"
```

### Available Modules

| Module | Contents |
|--------|----------|
| `math.flow` | sin, cos, sqrt, exp, log, etc. |
| `string.flow` | String manipulation, parsing |
| `collections.flow` | Vector, Stack, Queue, HashMap, Set |
| `net.flow` | TCP/UDP sockets, HTTP client |
| `concurrent.flow` | Threads, Mutex, Channels, Atomics |
| `posix.flow` | File I/O, processes, signals |
| `option.flow` | Option<T> type |
| `result.flow` | Result<T, E> type |
| `autodiff.flow` | Automatic differentiation |

---

## CLI Reference

```bash
./flow <command> [options] [file]

Commands:
  run <file>        Compile and run a program
  compile <file>    Compile to executable
  jit <file>        JIT compile and run
  mlir <file>       Generate MLIR
  mlir-run <file>   Compile via MLIR and run
  gpu <file>        Generate GPU shaders
  repl              Start interactive REPL
  init [name]       Initialize a new project
  add <package>     Add a dependency
  build             Build the project
  test              Run all tests
  fmt <file>        Format source code
  lsp               Start language server
```

---

## Next Steps

| Goal | Resource |
|------|----------|
| Learn the language in depth | [docs/LANGUAGE_SPEC.md](LANGUAGE_SPEC.md) |
| See more examples | [examples/](../examples/) |
| Understand effects | [docs/language/effects.md](language/effects.md) |
| Use autodiff | [docs/library/autodiff.md](library/autodiff.md) |
| Write GPU code | [examples/gpu/](../examples/gpu/) |
| Contribute | [docs/project/CONTRIBUTING.md](project/CONTRIBUTING.md) |

---

## Troubleshooting

### "command not found: flow"

Make sure you're in the FLOW directory and using `./flow` (with the dot-slash).

### "gcc not found"

Install a C compiler:
- macOS: `xcode-select --install`
- Ubuntu: `sudo apt install build-essential`
- Windows: Install MinGW or use WSL

### "MLIR commands fail"

MLIR features require LLVM. Install via:
- macOS: `brew install llvm`
- Ubuntu: `sudo apt install llvm-15`

Then add LLVM to your PATH.

---

Happy coding! 🚀
