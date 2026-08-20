# Functions

Functions use explicit parameter and return types. A function body is a normal Flow block, and `return` exits the function immediately.

Every `flow` block on this page is compiler-checked in CI.

## Basic functions

```flow
function add(a: i32, b: i32) -> i32 {
    return a + b
}

function square(x: f32) -> f32 {
    return x * x
}
```

A function returning no value uses `void`:

```flow
function do_nothing() -> void {
}
```

## Early return

```flow
function absolute_value(x: i32) -> i32 {
    if x < 0 {
        return -x
    }
    return x
}
```

## Calling functions

Executable statements live inside a function such as `main`:

```flow
function multiply(a: i32, b: i32) -> i32 {
    return a * b
}

function main() -> i32 {
    let result: i32 = multiply(6, 7)
    return result - 42
}
```

## Local mutation

Bindings are immutable unless declared with `let mut`. Function parameters are values; create a mutable local when an algorithm needs reassignment.

```flow
function sum_to(n: i32) -> i32 {
    let mut total: i32 = 0
    let mut i: i32 = 0

    while i <= n {
        total = total + i
        i = i + 1
    }

    return total
}
```

## Struct parameters and return values

```flow
struct Point {
    x: f32,
    y: f32
}

function move_point(p: Point, dx: f32, dy: f32) -> Point {
    return Point {
        x: p.x + dx,
        y: p.y + dy
    }
}
```

Structs are passed and returned by value unless the API uses a pointer or span explicitly.

## Pointers

```flow
struct Counter {
    value: i32
}

function increment(counter: ptr<Counter>) -> void {
    counter.value = counter.value + 1
}
```

Use pointer parameters when a function intentionally mutates caller-owned state.

## Fixed arrays

Flow's fixed-size array type is `array<T, N>`:

```flow
function sum4(values: array<i32, 4>) -> i32 {
    let mut total: i32 = 0
    for i in 0 to 4 {
        total = total + values[i]
    }
    return total
}
```

For borrowed variable-length views, use [`span<T>`](spans.md).

## Recursion

Ordinary recursion is supported in the general profile:

```flow
function factorial(n: i32) -> i32 {
    if n <= 1 {
        return 1
    }
    return n * factorial(n - 1)
}
```

Safety profiles can impose stricter whole-program rules; see [Safety profiles](safety-profiles.md).

## Effects in function signatures

A function that may perform an algebraic effect declares it in its effect row:

```flow
effect Log {
    write(value: i32) -> void
}

function record(value: i32) -> void with Log {
    Log.write(value)
}
```

See [Effects and capabilities](../effects-showcase.md) for handlers and capability implementations.

## Generics

Generic type parameters are declared after the function name:

```flow
function identity<T>(value: T) -> T {
    return value
}
```

The compiler specializes generic calls for concrete types.

## Function forms not yet part of current Flow

Tuple return syntax, ad-hoc function overloading by repeated names, and the old `[T]` dynamic-array notation appeared in early design documents but are not the current function surface. Documentation that discusses proposed syntax labels it explicitly as future or pseudocode rather than presenting it as runnable Flow.

## See also

[Syntax](syntax.md), [Types](types.md), [Spans](spans.md), [Effects](../effects-showcase.md), and the [language specification](../LANGUAGE_SPEC.md).