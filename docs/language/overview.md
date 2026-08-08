# Flow Language Overview

Flow is a statically-typed, compiled language built for performance and expressiveness. The thesis is that programs describe **systems evolving through time** ([vision](../vision.md)). Today that means a general-purpose core plus a shipped dynamics seed: the [`dsys` surface syntax](dynamics-dsl.md) and [dynamics library](../library/dynamics.md) for modeling, analyzing, and controlling linear systems.

## Key Features

| Feature | Description |
|---------|-------------|
| **Strong Types** | Compile-time type checking with generics |
| **Effects** | Algebraic effects for capability-based programming |
| **Autodiff** | Dual numbers + reverse helpers in stdlib; grad codegen for tiny nets (not a compiler `loss.grad` pass yet) |
| **C Backend** | Compiles to portable C for any platform |
| **Native Graphics** | macOS graphics via Metal/CoreGraphics |

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
