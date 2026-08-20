# Language Reference

Detailed documentation for the Flow programming language.

## Contents

| Document | Description |
|----------|-------------|
| [Spec Index](spec-index.md) | Navigable TOC into LANGUAGE_SPEC + focused pages |
| [Overview](overview.md) | Language philosophy and key features |
| [Syntax](syntax.md) | Lexical structure, operators, grammar |
| [Types](types.md) | Type system and primitive types |
| [Spans](spans.md) | Borrowed `{pointer, length}` views over contiguous storage |
| [Functions](functions.md) | Function definitions and calling |
| [Variables](variables.md) | Variables, mutability, scope |
| [Dynamics DSL](dynamics-dsl.md) | `dsys` / `analyze` / LQR expanders |
| [Ordering](ordering.md) | Declarative `\|> sort` / `sortBy` / `\|> find`, float total order |
| [Explainable compilation](explainable-compilation.md) | `--explain`: the plan, the costs, the failed constraints |
| [Graphics](graphics.md) | Native 2D graphics — macOS Cocoa; Linux/Windows SDL2 (+ stub) |
| [Shaders](shaders.md) | Fill-shader surface language (Metal on macOS) |
| [WebAssembly](wasm.md) | Near-term Flow→C→emscripten path; native Flow-in-WASM deferred |
| [Async via Effects](async-effects.md) | FiberAsync / ThreadedAsync / NetpollAsyncIO (no async/await) |
| [Concurrency vs Go](concurrency-vs-go.md) | Channels, fibers, OpenMP, measured benches |
| [Replacing Go](replace-go.md) | Scorecard for Go-shaped workloads |
| [Debugging](debugging.md) | `./flow debug`, `#line`, LLDB/GDB |
| [Modules](modules.md) | Named imports, package paths, `export import` re-export |
| [Module namespacing](modules-namespacing.md) | Why `module X { }` flattens, and what a real namespace would cost |
| [Language Design](language_design.md) | Design rationale |
| [Safety profiles](safety-profiles.md) | `--profile safety\|flight`, `@safe`/`@unsafe`, `FLOW_DIAG` |
| [Certification hub](../certification/README.md) | MISRA/CERT matrices, reproducible builds |
| [North-star](../vision/north-star.md) | Evolution / units design cards |

## Quick Reference

The common scalar types are `i32`, `i64`, `f32`, `f64`, `bool`, `string`, and `void`. Pointers use `ptr<T>` and fixed arrays use `array<T, N>`.

### Variable Declaration
```flow
let x: i32 = 42
let mut y: i32 = 0
```

### Function
```flow
function add(a: i32, b: i32) -> i32 {
    return a + b
}
```

### Struct
```flow
struct Point { x: f32, y: f32 }
let p: Point = Point { x: 1.0, y: 2.0 }
```

### Control Flow
```flow-pseudocode
if x > 0 { ... } elif x < 0 { ... } else { ... }
while condition { ... }
for i in 0 to n { ... }
parallel for i in 0 to n { ... }   # OpenMP when available
```
