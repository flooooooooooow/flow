# 3. Decisions and repetition

Control flow selects statements and repeats them. The condition of `if` and `while` has type `bool`. Every `flow` block in this chapter is compiler-checked in CI.

## 3.1 Selection

```flow
function sign(x: i32) -> i32 {
    if x < 0 {
        return -1
    } elif x > 0 {
        return 1
    } else {
        return 0
    }
}
```

Branches are tested from top to bottom. At most one branch executes. An early `return` ends the current function immediately.

For independent tests, use independent `if` statements:

```flow
function classify_temperature(temperature: f64, minimum: f64, maximum: f64) -> i32 {
    let mut flags: i32 = 0
    if temperature < minimum {
        flags = flags + 1
    }
    if temperature > maximum {
        flags = flags + 2
    }
    return flags
}
```

## 3.2 `while`

A `while` loop repeats while its condition remains true:

```flow
function first_power_at_least_100() -> i32 {
    let mut n: i32 = 1
    while n < 100 {
        n = n * 2
    }
    return n
}
```

Here `n` takes the values `1, 2, 4, 8, 16, 32, 64, 128` and stops at `128`.

## 3.3 `for` and half-open ranges

```flow
function sum_below_4() -> i32 {
    let mut total: i32 = 0
    for i in 0 to 4 {
        total = total + i
    }
    return total
}
```

The range is half-open: `0 to 4` contains `0`, `1`, `2`, and `3`, not `4`.

A step may be stated explicitly:

```flow
function even_sum() -> i32 {
    let mut total: i32 = 0
    for even in 0 to 10 step 2 {
        total = total + even
    }
    return total
}
```

## 3.4 Euclid's algorithm

```flow
function gcd(a0: i32, b0: i32) -> i32 {
    let mut a: i32 = a0
    let mut b: i32 = b0
    while b != 0 {
        let remainder: i32 = a % b
        a = b
        b = remainder
    }
    return a
}
```

At each iteration, `gcd(a, b) == gcd(b, a % b)`. The remainder is smaller than `b` for positive operands, so the process reaches zero.

A complete demonstration:

```flow
extern {
    function printf(fmt: string, ...) -> i32
}

function gcd_demo(a0: i32, b0: i32) -> i32 {
    let mut a: i32 = a0
    let mut b: i32 = b0
    while b != 0 {
        let remainder: i32 = a % b
        a = b
        b = remainder
    }
    return a
}

function main() -> i32 {
    let mut sum: i32 = 0
    for n in 0 to 10 {
        if n % 2 == 0 {
            sum = sum + n
        }
    }

    printf("even sum below 10: %d\n", sum)
    printf("gcd(84, 30): %d\n", gcd_demo(84, 30))

    if sum != 20 or gcd_demo(84, 30) != 6 {
        return 1
    }
    return 0
}
```

Source: [`examples/book/03_control.flow`](../../examples/book/03_control.flow)

```bash
FLOW_HOST=python ./flow run examples/book/03_control.flow
```

## 3.5 Choosing a loop

| Situation | Form |
|---|---|
| Number of iterations follows an integer range | `for` |
| Termination depends on changing state | `while` |
| Exactly one of several conditions should run | `if` / `elif` / `else` |
| A function has already determined its result | early `return` |

## Exercises

Sum all multiples of three below `100`; count how many divisions by two reduce `1024` to `1`; extend `gcd` with a negative-input policy; then write and test a three-way `classify(x)` function.

Next: [Functions](04-functions.md).
