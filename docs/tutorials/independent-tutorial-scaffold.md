# Independent Flow Tutorial Scaffold

This scaffold provides a ready-to-use template for community authors writing independent tutorials for the Flow programming language. Follow this structure to create clear, reproducible, and runnable tutorials.

## 1. Introduction

Flow is a statically typed, compiled systems programming language designed for systems that evolve through time. Its core language features zero-cost abstractions, deterministic compilation to C, and native support for continuous state evolution.

### Installation & Environment

To run Flow code, install the toolchain or clone the repository:

```bash
brew tap flooooooooooow/flow
brew install flow
flow version
```

Alternatively, build from source:

```bash
git clone https://github.com/flooooooooooow/flow.git
cd flow
./flow run examples/basics/hello_world.flow
```

## 2. Hello World

A minimal, complete Flow program defines an entry point `main` returning an `i32` exit code.

```flow
function main() -> i32 {
    println("Hello, Flow!")
    return 0
}
```

Run this file using:

```bash
flow run hello.flow
```

## 3. Variables, Functions, and Control Flow

Flow supports immutable bindings with `let` and mutable bindings with `let mut`. Functions use explicit type annotations and arrow `->` return types.

```flow
function add(a: i32, b: i32) -> i32 {
    return a + b
}

function main() -> i32 {
    let mut total: i32 = 0
    total = add(total, 42)

    if total > 0 {
        printf("total = %d\n", total)
    } else {
        println("zero or negative")
    }

    return 0
}
```

## 4. Conventional Algorithm

Flow handles loops, ranges, and recursive or iterative algorithms cleanly. Here is a Fibonacci calculation using recursion and range-based loops:

```flow
function fibonacci(n: i32) -> i32 {
    if n <= 1 {
        return n
    }
    return fibonacci(n - 1) + fibonacci(n - 2)
}

function main() -> i32 {
    for i in 0..8 {
        printf("fib(%d) = %d\n", i, fibonacci(i))
    }
    return 0
}
```

## 5. Flow's Evolution Model

Flow introduces `flow` blocks for modeling continuous dynamics through state variables and differential relationships (`evolves as`). The compiler automatically synthesizes state constructors and numerical integration steps.

```flow
flow HarmonicOscillator {
    state x: f64 = 1.0
    state v: f64 = 0.0
    param k: f64 = 1.0

    x evolves as v
    v evolves as -k * x
}

function main() -> i32 {
    let mut sys = HarmonicOscillator_new()
    let dt: f64 = 0.01

    for _ in 0..10 {
        HarmonicOscillator_step(&sys, dt)
    }

    printf("x = %.2f, v = %.2f\n", sys.x, sys.v)
    return 0
}
```

## 6. Author Observations & Verification

When publishing an independent tutorial:

- **What Surprised You:** Note any syntax choices, pipeline operations (`|>`), or compiler messages that stood out.
- **Experimental Features:** Mention any domain surfaces or experimental backends (e.g. GPU, MLIR) tested during writing.
- **Tested Environment:**
  - **Flow Version:** Flow 1.0.2
  - **Platform:** macOS / Linux (x86_64 / arm64)
  - **Verification:** Every code block verified with `./flow run` and `python3 scripts/check_doc_examples.py`.
