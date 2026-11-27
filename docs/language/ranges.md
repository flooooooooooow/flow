# Ranges and range algebra

A range is an arithmetic progression written `start..end step stride`. The end
is exclusive and the stride defaults to `1`, so `0..5` is `0 1 2 3 4`.

Ranges drive `for` loops:

```flow
function main() -> i32 {
    for i in 0..5 {
        println(i)
    }
    for i in 0..20 step 5 {
        println(i)
    }
    return 0
}
```

A negative stride counts down. The end stays exclusive:

```flow
function countdown() -> i32 {
    let mut last: i32 = 0
    for i in 10..0 step -3 {
        last = i
    }
    return last
}

function main() -> i32 {
    println(countdown())
    return 0
}
```

## sum

`sum` takes a range and returns the total of its elements without iterating.
The compiler applies the closed form for an arithmetic progression, so the cost
does not depend on how many elements the range has.

```flow
function main() -> i32 {
    println(sum(0..101))
    println(sum(0..1000 step 3))
    return 0
}
```

The native parser records the range as a special call, not a folded literal.
The C emitter generates a closed-form helper call; MLIR emission has a
literal-folding path and a runtime helper path. Each bound expression is
passed as a single argument on the C path:

```flow
function triangle(n: i32) -> i32 {
    return sum(0..n + 1)
}

function main() -> i32 {
    println(triangle(100))
    return 0
}
```

A runtime stride of `0` produces zero in the C helper; the language regression
explicitly checks this. Do not rely on a compile-time diagnostic for zero stride.

## Union and intersection

Two ranges compose with `|` for union and `&` for intersection. The result is
still a set of integers, so `sum` reduces it the same way:

```flow
function main() -> i32 {
    println(sum(0..1000 step 3 | 0..1000 step 5))
    println(sum(0..1000 step 3 & 0..1000 step 5))
    return 0
}
```

The first line is "the sum of every multiple of 3 or 5 below 1000". The second
is the sum of the multiples of 15, since the intersection of two arithmetic
progressions is itself an arithmetic progression whose stride is the least
common multiple of the two strides.

Union follows inclusion-exclusion, so elements shared by both ranges are
counted once:

```flow
function main() -> i32 {
    # evens below 20 sum to 90, multiples of 3 to 63, multiples of 6 to 36
    println(sum(0..20 step 2 | 0..20 step 3))
    return 0
}
```

The native range-sum parser accepts one set operator between two ranges.
This does not establish precedence for chained range algebra.

Inside `sum(...)`, `|` and `&` between two ranges mean union and intersection.
Everywhere else they keep their bitwise meaning. The bounds themselves parse at
equality precedence, so `sum(0..n - 1 step 2)` still subtracts and only a `|`
or `&` that separates two ranges reads as set algebra.

## Difference

There is no difference operator. Write it with the identity:

```flow
function main() -> i32 {
    # multiples of 3 below 1000 that are not multiples of 5
    println(sum(0..1000 step 3) - sum(0..1000 step 3 & 0..1000 step 5))
    return 0
}
```

## Limits

Ranges are not yet values. A range cannot be bound to a variable, stored in a
struct, passed to a function or returned from one. It exists only in the two
positions that consume it directly: the header of a `for` loop, and the
argument of `sum`.

The native parser handles one or two ranges for both literal and runtime
bounds. It requires the closing parenthesis after the second range; do not
rely on historical multi-range folding. Combine sums by hand instead:

```flow
function three_ways(n: i32) -> i32 {
    let a: i32 = sum(0..n step 2 | 0..n step 3)
    let c: i32 = sum(0..n step 5)
    let overlap: i32 = sum(0..n step 2 & 0..n step 5)
        + sum(0..n step 3 & 0..n step 5)
        - sum(0..n step 30)
    return a + c - overlap
}

function main() -> i32 {
    println(three_ways(100))
    return 0
}
```
