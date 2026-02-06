# Language Reference

Detailed documentation for the Flow programming language.

## Contents

| Document | Description |
|----------|-------------|
| [Overview](overview.md) | Language philosophy and key features |
| [Syntax](syntax.md) | Lexical structure, operators, grammar |
| [Types](types.md) | Type system and primitive types |
| [Functions](functions.md) | Function definitions and calling |
| [Variables](variables.md) | Variables, mutability, scope |
| [Graphics](graphics.md) | Native graphics API (macOS) |
| [Language Design](language_design.md) | Design rationale |

## Quick Reference

### Types
```
i32, i64, f32, f64, bool, string, void
ptr<T>, array<T, N>
```

### Variable Declaration
```flow
let x: i32 = 42           # Immutable
let mut y: i32 = 0        # Mutable
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
```flow
if x > 0 { ... } elif x < 0 { ... } else { ... }
while condition { ... }
for i in 0 to n { ... }
```
