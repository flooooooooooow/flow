# 3. Decisions and repetition

Control flow selects statements and repeats them. The condition of `if` and
`while` has type `bool`.

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

Branches are tested from top to bottom. At most one branch executes. An early
`return` ends the current function immediately.

For independent tests, use independent `if` statements:

```flow
if temperature < minimum {
    println("below range")
}
if temperature > maximum {
    println("above range")
}
```

## 3.2 `while`

A `while` loop repeats while its condition remains true:

```flow
let mut n: i32 = 1
while n < 100 {
    n = n * 2
}
```

The loop has three obligations:

1. establish the initial state;
2. state the continuation condition;
3. update some value so that the condition can eventually become false.

Here `n` takes the values `1, 2, 4, 8, 16, 32, 64, 128`. The loop body runs
seven times and stops with `n == 128`.

## 3.3 `for` and half-open ranges

```flow
for i in 0 to 4 {
    print(i)
}
```

The range is half-open. It contains `0`, `1`, `2`, and `3`, but not `4`.
Therefore an array with four elements can be traversed by `0 to 4`.

A step may be stated explicitly:

```flow
for even in 0 to 10 step 2 {
    print(even)
}
```

The induction variable belongs to the loop body and should be treated as a
value supplied by the loop, not as mutable program state.

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

At each iteration, `gcd(a, b) == gcd(b, a % b)`. The remainder is smaller
than `b` when both operands are positive, so the process reaches zero.

The complete demonstration combines selection, a `for` loop, a `while` loop,
and a self-check:

```flow from=examples/book/03_control.flow
extern {
    function printf(fmt: string, ...) -> i32
}

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

function main() -> i32 {
    let mut sum: i32 = 0
    for n in 0 to 10 {
        if n % 2 == 0 {
            sum = sum + n
        }
    }

    printf("even sum below 10: %d\n", sum)
    printf("gcd(84, 30): %d\n", gcd(84, 30))

    if sum != 20 or gcd(84, 30) != 6 {
        return 1
    }
    return 0
}
```

Source:
[`examples/book/03_control.flow`](../../examples/book/03_control.flow)

```bash
./flow run examples/book/03_control.flow
```

Output:

```text
even sum below 10: 20
gcd(84, 30): 6
```

## 3.5 Choosing a loop

| Situation | Form |
|---|---|
| Number of iterations follows an integer range | `for` |
| Termination depends on changing state | `while` |
| Exactly one of several conditions should run | `if` / `elif` / `else` |
| A function has already determined its result | early `return` |

## Exercises

1. Sum all multiples of three below `100`.
2. Count how many divisions by two reduce `1024` to `1`.
3. Extend `gcd` with a precondition check for negative inputs.
4. Write `classify(x)` returning `-1`, `0`, or `1`, then test all branches
   from `main`.

Next: [Functions](04-functions.md).

