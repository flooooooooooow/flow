# 2. Values and types

A type defines the values an expression may produce and the operations allowed on those values. Flow checks these rules before native execution. Every `flow` block in this chapter is compiler-checked in CI.

## 2.1 Primitive types

The central primitive types are:

| Type | Purpose | Example |
|---|---|---|
| `i8`, `i16`, `i32`, `i64` | signed integers | `-17` |
| `u8`, `u16`, `u32`, `u64` | unsigned integers | `255` |
| `f32`, `f64` | floating-point values | `3.14159` |
| `bool` | logical truth | `true` |
| `string` | text | `"ready"` |
| `void` | no returned value | function return type |

Use a type whose range and precision match the quantity. `i32` is the ordinary choice for small counts and status values. `f64` is the ordinary choice for numerical models where accumulated rounding error matters.

## 2.2 Bindings

`let` introduces an immutable local binding:

```flow
function binding_example() -> i32 {
    let sample_count: i32 = 4
    let celsius: f64 = 21.5
    let ready: bool = true
    let label: string = "room A"

    if ready and celsius > 0.0 and label == "room A" {
        return sample_count
    }
    return 0
}
```

When the initializer gives sufficient information, the compiler can infer the type:

```flow
function inferred_values() -> i32 {
    let sample_count = 4
    let celsius = 21.5
    if celsius > 20.0 {
        return sample_count
    }
    return 0
}
```

Explicit types are useful at interfaces, in numerical work, and whenever a reader should not have to infer intent from a literal.

## 2.3 Mutation

State that changes must be declared with `let mut`:

```flow
function accumulated_total() -> f64 {
    let mut total: f64 = 87.5
    total = total + 1.0
    return total
}
```

The following program is rejected, and CI checks that rejection:

```flow expect-error
function immutable_assignment() -> f64 {
    let total: f64 = 87.5
    total = 88.5
    return total
}
```

Mutability is local information. A reader can distinguish a fixed input from evolving state at its declaration.

## 2.4 Arithmetic and comparison

Arithmetic uses conventional precedence:

```flow
function arithmetic_example() -> i32 {
    let a: i32 = 2 + 3 * 4
    let b: i32 = (2 + 3) * 4
    let q: i32 = 17 / 5
    let r: i32 = 17 % 5
    return a + b + q + r
}
```

Floating-point division and comparisons are equally direct:

```flow
function comparison_example(x: f64) -> bool {
    let quotient: f64 = 17.0 / 5.0
    let within: bool = x >= 0.0 and x <= 10.0
    let outside: bool = x < 0.0 or x > 10.0
    let different: bool = x != quotient
    return within and not outside and different
}
```

`and` and `or` short-circuit. In `a and b`, `b` is evaluated only when `a` is true. In `a or b`, `b` is evaluated only when `a` is false.

## 2.5 A complete measurement

```flow
extern {
    function printf(fmt: string, ...) -> i32
}

function main() -> i32 {
    let celsius: f64 = 21.5
    let fahrenheit: f64 = celsius * 9.0 / 5.0 + 32.0
    let sample_count: i32 = 4
    let mut total: f64 = 87.5
    total = total + 1.0
    let mean: f64 = total / 4.0
    let comfortable: bool = celsius >= 18.0 and celsius <= 24.0

    printf("samples: %d\n", sample_count)
    printf("mean: %.3f C\n", mean)
    printf("converted: %.1f F\n", fahrenheit)
    printf("comfortable: %d\n", comfortable)
    return 0
}
```

Source: [`examples/book/02_values.flow`](../../examples/book/02_values.flow)

```bash
FLOW_HOST=python ./flow run examples/book/02_values.flow
```

## 2.6 Casts

Use `as` when a conversion must be explicit:

```flow
function average(total: f64, count: i32) -> f64 {
    let count_f: f64 = count as f64
    return total / count_f
}
```

A cast records the point at which representation changes. It does not repair an invalid value. Before narrowing a large integer or a floating-point value, establish that the destination range is adequate.

## Exercises

Convert `68.0` degrees Fahrenheit to Celsius; compute the mean of five fixed readings with one mutable accumulator; write a Boolean expression for values in `[10.0, 20.0)`; and verify the values of `7 / 2`, `7.0 / 2.0`, and `7 % 2`.

Next: [Decisions and repetition](03-decisions-and-repetition.md).
