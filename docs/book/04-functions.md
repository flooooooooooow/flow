# 4. Functions

A function gives a name and a type to a computation. Its signature is a
contract between callers and the implementation.

```flow
function clamp(x: f64, lo: f64, hi: f64) -> f64
```

The function accepts three `f64` arguments and returns one `f64` value.

## 4.1 Parameters and results

```flow
function square(x: f64) -> f64 {
    return x * x
}

function report_ready() -> void {
    println("ready")
}
```

Every non-`void` path must return a value compatible with the declared result
type. A `void` function performs an action without contributing a value to its
caller.

Arguments are evaluated before the call:

```flow
let area: f64 = square(width + margin)
```

The expression `width + margin` is evaluated first; its result becomes `x` in
`square`.

## 4.2 Small contracts

Functions are easiest to reason about when each has one stable responsibility:

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

The function establishes the postcondition `lo <= result <= hi`, provided
that `lo <= hi`.

## 4.3 Composition

Larger operations can be expressed by calls to smaller ones:

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

function pow_i(base: f64, exponent: i32) -> f64 {
    let mut result: f64 = 1.0
    for n in 0 to exponent {
        result = result * base
    }
    return result
}

function compound(principal: f64, rate: f64, years: i32) -> f64 {
    return principal * pow_i(1.0 + clamp(rate, 0.0, 1.0), years)
}
```

The nested expression is evaluated from the inside:

```text
clamp(rate, 0.0, 1.0)
1.0 + clamped_rate
pow_i(growth_factor, years)
principal * growth
```

Complete demonstration:

```flow
extern {
    function printf(fmt: string, ...) -> i32
}

function clamp(x: f64, lo: f64, hi: f64) -> f64 {
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
    return principal * pow_i(1.0 + clamp(rate, 0.0, 1.0), years)
}

function main() -> i32 {
    let balance: f64 = compound(1000.0, 0.05, 3)
    printf("balance after 3 years: %.2f\n", balance)
    return 0
}
```

Source:
[`examples/book/04_functions.flow`](../../examples/book/04_functions.flow)

```bash
./flow run examples/book/04_functions.flow
```

```text
balance after 3 years: 1157.63
```

## 4.4 Recursion

A function may call itself:

```flow
function factorial(n: i32) -> i32 {
    if n <= 1 {
        return 1
    }
    return n * factorial(n - 1)
}
```

The base case ends recursion. The recursive case must move toward that base
case. Without both properties, the call chain does not terminate.

For simple numeric iteration, a loop usually makes storage and termination
more evident. Recursion is natural for inductive data, tree traversal, and
algorithms whose definition is recursive.

## 4.5 Forward references

Function declarations are resolved across the source module. Mutually
recursive functions can therefore refer to one another:

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

Such definitions still require a domain restriction. The example is defined
for nonnegative `n`; negative input would move away from the base case.

## Exercises

1. Write `lerp(a, b, t)` for linear interpolation.
2. Write `pow_i` using a `while` loop.
3. Add an explicit check that rejects a negative exponent.
4. Define `sum_to(n)` both iteratively and recursively. Compare their base
   cases and state changes.

Next: [Records and fixed arrays](05-records-and-arrays.md).
