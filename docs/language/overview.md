# Flow Language Overview

Flow is a statically-typed, compiled language designed for performance and expressiveness — built on the thesis that programs describe **systems evolving through time** ([vision](../vision.md)). Today that means a general-purpose core plus a shipped dynamics seed: the [`dsys` surface syntax](dynamics-dsl.md) and [dynamics library](../library/dynamics.md) for modeling, analyzing, and controlling linear systems.

## Key Features

| Feature | Description |
|---------|-------------|
| **Strong Types** | Compile-time type checking with generics |
| **Effects** | Algebraic effects for capability-based programming |
| **Autodiff** | Dual numbers + reverse helpers in stdlib; grad codegen for tiny nets (not a compiler `loss.grad` pass yet) |
| **Complex Numbers** | `c64`/`c128` types map to C99 `_Complex`. Constructors, arithmetic, and `creal`/`cimag`/`cabs`/`cexp` builtins. |
| **C Backend** | Compiles to portable C for any platform |
| **Native Graphics** | macOS graphics via Metal/CoreGraphics |
| **Safety Profile** | `--profile safety` adds MISRA/CERT-derived overflow checks, div0 guards, shift UB rejection. `--emit-manifest` produces a compliance report. |

## Quick Example

```flow
function main() -> i32 {
    let x: i32 = 42
    println(x)
    return 0
}
```

## Documentation

- **[Getting Started](../getting-started.md)** - Installation and first program
- **[Syntax](syntax.md)** - Grammar and lexical structure
- **[Types](types.md)** - Type system reference
- **[Functions](functions.md)** - Function definitions
- **[Variables](variables.md)** - Variables and mutability
- **[flow-verify](../third-party/flow-verify.md)** - optional formal math library (not core Flow)

## Design Philosophy

1. **Explicit over Implicit** - `let mut` for mutable, clear type annotations
2. **Zero-Cost Abstractions** - High-level features compile efficiently
3. **Effects for Side Effects** - Controlled capabilities, not global state
4. **C Interop** - Easy FFI with C libraries
