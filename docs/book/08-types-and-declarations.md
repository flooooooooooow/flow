# 8. Types and declarations beyond the core

Flow has wide integers, complex values, nominal types, units, generics, enums, traits, constants, module state, and code-generation attributes. Every `flow` block in this chapter is compiler-checked in CI.

## 8.1 Complete scalar set

| Family | Types |
|---|---|
| Signed integers | `i8`, `i16`, `i32`, `i64`, `i128` |
| Unsigned integers | `u8`, `u16`, `u32`, `u64`, `u128` |
| Floating point | `f32`, `f64` |
| Complex | `c64`, `c128` |
| Logical | `bool` |
| Text | `string` |
| Empty result | `void` |

```flow
function scalar_demo() -> f64 {
    let mask: u64 = 0xFFFF
    let large: i128 = 9000000000000000000 as i128
    let z: c128 = c128(3.0, 4.0)
    let magnitude: f64 = cabs(z)
    if mask > 0 and large > 0 {
        return magnitude
    }
    return 0.0
}
```

## 8.2 Floating-point order

Ordinary comparisons use IEEE rules. Declarative sorting uses a deterministic IEEE total order so NaNs and signed zero have stable positions. See [`tests/lang/test_sort_nan.flow`](../../tests/lang/test_sort_nan.flow).

## 8.3 Composite type forms

The current spellings are `array<T>` for dynamic arrays, `array<T, N>` for fixed arrays, `ptr<T>` for pointers, `span<T>` / `span<mut T>` / `span<T, N>` for borrowed views, `vec<T, N>` for the partially supported SIMD vector surface, and `(A, B) -> R` for function/closure types. `&[T]`, `&mut [T]`, and `&[T; N]` are span sugar.

## 8.4 Aliases and distinct types

```flow
type Bytes = array<u8>
distinct type UserId = i64

function stored_id(raw: i64) -> i64 {
    let user: UserId = raw as UserId
    return user as i64
}
```

Aliases are transparent. Distinct types form a nominal boundary crossed explicitly with `as`.

## 8.5 Units of measure

```flow
unit Meter
unit Second
unit Velocity = Meter / Second
unit Acceleration = Meter / Second^2

function measured_speed() -> Velocity {
    let distance: Meter = 100.0 as Meter
    let duration: Second = 8.0 as Second
    return distance / duration
}
```

Units compose through multiplication/division, require compatible dimensions for addition/comparison, and erase to numeric storage at runtime.

## 8.6 Constants and module statics

```flow
struct Node {
    value: i32
}

const BLOCK_SIZE: i32 = 256
let mut calls: i32 = 0
let mut table: array<i32, 4> = [0, 0, 0, 0]
let mut head: ptr<Node> = null

function bump_calls() -> i32 {
    calls = calls + 1
    return calls
}
```

`const` is compile-time immutable state. Top-level `let mut` is private file-scope mutable state in the C backend and requires an explicit type plus constant initializer.

## 8.7 Enums

```flow
enum Direction {
    North,
    South,
    East,
    West
}

function north_tag() -> i32 {
    return Direction_North as i32
}
```

## 8.8 Generics

```flow
struct Box<T> {
    value: T
}

function identity<T>(x: T) -> T {
    return x
}

function generic_answer() -> i32 {
    let box: Box<i32> = Box<i32> { value: 42 }
    return identity<i32>(box.value)
}
```

The compiler monomorphises used concrete type combinations.

## 8.9 Function overloading

```flow
function pick(value: i32) -> i32 { return 1 }
function pick(value: u32) -> i32 { return 2 }
```

Resolution uses argument types and the C backend mangles the chosen signature.

## 8.10 Traits and implementations

```flow
struct ComparablePoint {
    x: i32,
    y: i32
}

trait Comparable {
    function compare(self: ComparablePoint, other: ComparablePoint) -> i32
}

impl Comparable for ComparablePoint {
    function compare(self: ComparablePoint, other: ComparablePoint) -> i32 {
        if self.x < other.x { return -1 }
        if self.x > other.x { return 1 }
        return 0
    }
}
```

Trait-driven dispatch remains partial across hosts; ordinary named functions remain the portable baseline.

## 8.11 Function attributes

A function attribute precedes the declaration. Use only implemented attributes; speculative attributes belong in `flow-future` examples.

```flow
@always_inline
function add_fast(a: i32, b: i32) -> i32 {
    return a + b
}
```

Implemented attribute families include build guards (`@only`, `@guard`, `@compile`), inlining (`@inline`, `@always_inline`, `@noinline`), target selection (`@target`), ABI control (`@flow_api`), device code (`@gpu`), RT safety (`@rt_safe`), lifetime domains (`@lifetime`), and safety boundaries (`@safe`, `@unsafe`).

## 8.12 Debug and expectation forms

```flow
function compute() -> i32 {
    return 42
}

function checked_compute() -> i32 {
    let measured: i32 = dbg compute()
    expect measured >= 0
    return measured
}
```

On the C backend `dbg` writes a diagnostic and yields its operand; `expect` aborts if its Boolean condition is false. Backend diagnostic behavior differs, so executable repository tests still use explicit `main` return codes for portable pass/fail behavior.

## Exercises

Define distinct input/output index types; derive dimensions for mass and force; instantiate generic containers with several types; and compare generic/enum behavior across compiler hosts.

Next: [Expressions, matching, and declarative operations](09-expressions-and-matching.md).
