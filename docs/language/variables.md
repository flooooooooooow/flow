# Variables

Flow uses `let` for immutable bindings and `let mut` for mutable variables.

## Immutable Variables

```flow
let x: i32 = 42
let name: string = "Flow"
let pi: f64 = 3.14159
```

Type inference works for most cases:

```flow
let x = 42        # Inferred as i32
let y = 3.14      # Inferred as f64
let flag = true   # Inferred as bool
```

## Mutable Variables

Use `let mut` when you need to change a value:

```flow
let mut counter: i32 = 0
counter = counter + 1

let mut sum: f64 = 0.0
sum = sum + 10.5
```

## Struct Field Assignment

```flow
struct Point {
    x: f32,
    y: f32
}

function main() -> i32 {
    let mut p: Point = Point { x: 0.0, y: 0.0 }
    p.x = 10.0
    p.y = 20.0
    return 0
}
```

## Array Elements

```flow
function main() -> i32 {
    let arr: array<i32, 5> = [1, 2, 3, 4, 5]
    # Note: array elements accessed via pointer for mutation
    return arr[0]
}
```

## Constants

For compile-time constants (not yet implemented, use `let` for now):

```flow
let PI: f64 = 3.14159265359
let MAX_SIZE: i32 = 1024
```

## Scope

Variables are block-scoped:

```flow
function demo() -> i32 {
    let x: i32 = 10
    
    if x > 5 {
        let y: i32 = 20   # Only visible in this block
        return x + y
    }
    
    # y is not accessible here
    return x
}
```
