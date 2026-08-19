# Type System

Flow is statically typed. Types are checked before code generation, and the compiler rejects incompatible assignments, calls, field accesses, and returns.

Every block labelled `flow` on this page is compiler-checked in CI.

## Primitive types

The core numeric and scalar types are `i8`, `i16`, `i32`, `i64`, `u8`, `u16`, `u32`, `u64`, `f32`, `f64`, `c64`, `c128`, `bool`, `string`, and `void`.

```flow
function scalar_examples() -> i32 {
    let signed: i32 = -42
    let wide: i64 = 9000000000
    let ratio: f64 = 3.141592653589793
    let ready: bool = true
    let label: string = "flow"

    if ready and signed < 0 and wide > 0 and ratio > 3.0 and label == "flow" {
        return 0
    }
    return 1
}
```

Complex constructors and arithmetic use `c64` and `c128`:

```flow
function complex_example() -> c64 {
    let a: c64 = c64(1.0, 2.0)
    let b: c64 = c64(3.0, -1.0)
    return a + b
}
```

## Type annotations and inference

Local bindings may state their type explicitly or let the compiler infer it from an initializer.

```flow
function inference_example() -> i32 {
    let explicit: i32 = 42
    let inferred = 10
    return explicit + inferred - 52
}
```

Use `let mut` when a binding will be reassigned:

```flow
function count_to(limit: i32) -> i32 {
    let mut value: i32 = 0
    while value < limit {
        value = value + 1
    }
    return value
}
```

## Fixed-size arrays

The current fixed-size array spelling is `array<T, N>`.

```flow
function sum4(values: array<i32, 4>) -> i32 {
    let mut total: i32 = 0
    for i in 0 to 4 {
        total = total + values[i]
    }
    return total
}
```

Array literals infer their element type and extent when enough context is available:

```flow
function first_value() -> i32 {
    let values: array<i32, 4> = [10, 20, 30, 40]
    return values[0]
}
```

The old `[T]` and `[T; N]` spellings appear in historical material but are not the current Flow type syntax.

## Spans

A `span<T>` is a borrowed view over contiguous storage. It does not own or allocate its elements.

```flow
function first(samples: span<f32>) -> f32 {
    return samples[0]
}
```

Mutable spans use `span<mut T>`. See [Spans](spans.md) for slicing, static extents, and lifetime checking.

## Structs

```flow
struct Point {
    x: f32,
    y: f32
}

struct Rectangle {
    origin: Point,
    width: f32,
    height: f32
}

function rectangle_area(rect: Rectangle) -> f32 {
    return rect.width * rect.height
}
```

Struct literals name every field:

```flow
struct Point2 {
    x: f32,
    y: f32
}

function make_point() -> Point2 {
    return Point2 { x: 3.0, y: 4.0 }
}
```

## Pointers

`ptr<T>` is an explicit pointer type used for FFI and mutable caller-owned state.

```flow
struct Counter {
    value: i32
}

function increment(counter: ptr<Counter>) -> void {
    counter.value = counter.value + 1
}
```

`ptr<void>` is the untyped pointer used at ABI boundaries.

## Type aliases

A transparent alias gives an existing type another name:

```flow
type Sample = f32

function silence() -> Sample {
    return 0.0
}
```

A distinct type is intentionally not interchangeable with its representation without an explicit conversion:

```flow
distinct type UserId = i64

function raw_id(id: UserId) -> i64 {
    return id as i64
}
```

## Generic functions and structs

Flow supports generic declarations that are specialized for concrete uses.

```flow
function identity<T>(value: T) -> T {
    return value
}
```

```flow
struct Pair<T> {
    first: T,
    second: T
}
```

## Units of measure

A `unit` declaration creates a dimension-carrying numeric type. Units erase to numeric storage in generated C, while dimensional compatibility is checked at compile time.

```flow
unit Meter
unit Second
unit Velocity = Meter / Second

function speed(distance: Meter, duration: Second) -> Velocity {
    return distance / duration
}
```

Construct a unit value with `as`:

```flow
unit Hertz

function carrier() -> Hertz {
    return 1000.0 as Hertz
}
```

Incompatible unit arithmetic is a compile-time error and should be shown as an explicit negative test, not as supposedly runnable code.

## RF aliases

The RF standard library uses complex samples and rate-tagged types. A transparent IQ alias can be declared as:

```flow
type IQ = c64

function iq_zero() -> IQ {
    return c64(0.0, 0.0)
}
```

Opaque sample domains can use a distinct type:

```flow
distinct type IQSample = c64
```

## Function types and proposed sum types

First-class function-value syntax, tuple returns, union types such as `i32 | f32`, and generic optional types are not part of the current stable type surface. When design documents discuss those forms, their fences are labelled `flow-future` rather than `flow`.

## Type safety

The compiler checks struct fields, function parameter and return types, array element types, pointer targets, units, distinct types, effects, and lifetime-domain constraints. Deliberately invalid examples belong in `flow expect-error` fences so CI verifies that the compiler continues to reject them.

## See also

[Functions](functions.md), [Spans](spans.md), [Lifetime domains](lifetime-domains.md), [Syntax](syntax.md), and the [language specification](../LANGUAGE_SPEC.md).