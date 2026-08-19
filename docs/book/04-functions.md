# 4. Functions

A function gives a name and a type to a computation. Its signature is a contract between callers and the implementation. Every `flow` block in this chapter is compiler-checked in CI.

```flow
function clamp_signature_example(x: f64, lo: f64, hi: f64) -> f64 {
    if x < lo { return lo }
    if x > hi { return hi }
    return x
}
```

## 4.1 Parameters and results

```flow
function square(x: f64) -> f64 {
    return x * x
}

function report_ready() -> void {
    println("ready")
}
```

Every non-`void` path must return a value compatible with the declared result type. A `void` function performs an action without contributing a value to its caller.

Arguments are evaluated before the call:

```flow
function square_area(width: f64, margin: f64) -> f64 {
    return square(width + margin)
}
```

The expression `width + margin` is evaluated first; its result becomes `x` in `square`.

## 4.2 Small contracts

```flow
function clamp(x: f64, lo: f64, hi: f64) -> f64 {
    if x < lo {
        return lo
    }
    if x > hi {
        return hi
    }
    return x
}
```

The function establishes `lo <= result <= hi` provided `lo <= hi`.

## 4.3 Composition

```flow
function clamp_rate(x: f64, lo: f64, hi: f64) -> f64 {
    if x < lo { return lo }
    if x > hi { return hi }
    return x
}

function pow_i(base: f64, exponent: i32) -> f64 {
    let mut result: f64 = 1.0
    for n in 0 to exponent {
        result = result * base
    }
    return result
}

function compound(principal: f64, rate: f64, years: i32) -> f64 {
    return principal * pow_i(1.0 + clamp_rate(rate, 0.0, 1.0), years)
}
```

The nested expression first clamps `rate`, then computes the growth factor, then raises it with `pow_i`, then multiplies by `principal`.

Complete demonstration:

```flow
extern {
    function printf(fmt: string, ...) -> i32
}

function clamp_demo(x: f64, lo: f64, hi: f64) -> f64 {
    if x < lo { return lo }
    if x > hi { return hi }
    return x
}

function pow_demo(base: f64, exponent: i32) -> f64 {
    let mut result: f64 = 1.0
    for n in 0 to exponent {
        result = result * base
    }
    return result
}

function compound_demo(principal: f64, rate: f64, years: i32) -> f64 {
    return principal * pow_demo(1.0 + clamp_demo(rate, 0.0, 1.0), years)
}

function main() -> i32 {
    let balance: f64 = compound_demo(1000.0, 0.05, 3)
    printf("balance after 3 years: %.2f\n", balance)
    return 0
}
```

Source: [`examples/book/04_functions.flow`](../../examples/book/04_functions.flow)

```bash
FLOW_HOST=python ./flow run examples/book/04_functions.flow
```

## 4.4 Recursion

```flow
function factorial(n: i32) -> i32 {
    if n <= 1 {
        return 1
    }
    return n * factorial(n - 1)
}
```

The base case ends recursion. The recursive case must move toward that base case.

## 4.5 Forward references

Function declarations are resolved across the source module, so mutually recursive functions can refer to one another:

```flow
function even(n: i32) -> bool {
    if n == 0 { return true }
    return odd(n - 1)
}

function odd(n: i32) -> bool {
    if n == 0 { return false }
    return even(n - 1)
}
```

The example is defined for nonnegative `n`; negative input would move away from the base case.

## Exercises

Write `lerp(a, b, t)`, rewrite `pow_i` with `while`, define a policy for negative exponents, and implement `sum_to(n)` both iteratively and recursively.

Next: [Records and fixed arrays](05-records-and-arrays.md).
