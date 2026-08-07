# Pipelines

Thread a value through calls with `|>`, pin it with `_`, and declare ordering
intent with `|> sort` / `sortBy`.

Prerequisites: [functions.md](functions.md), [arrays.md](arrays.md).

## Part 1: The pipeline operator

### 1.1 Prepend into a call

`x |> f(y)` lowers to `f(x, y)`. Chains are left-associative:
`a |> f() |> g()` is `g(f(a))`.

```flow
function double(x: i32) -> i32 {
    return x * 2
}

function add(a: i32, b: i32) -> i32 {
    return a + b
}

function main() -> i32 {
    let a: i32 = 21 |> double()
    let b: i32 = 10 |> add(32)
    printf("a=%d b=%d\n", a, b)
    return 0
}
```

### 1.2 Bare function name

`x |> f` is the same as `x |> f()`:

```flow
function negate(x: i32) -> i32 {
    return 0 - x
}

function main() -> i32 {
    let v: i32 = 7 |> negate
    printf("%d\n", v)
    return 0
}
```

### 1.3 Placeholder `_`

When the piped value is not the first argument, mark the slot with `_`:

```flow
function clamp(lo: i32, x: i32, hi: i32) -> i32 {
    if x < lo {
        return lo
    }
    if x > hi {
        return hi
    }
    return x
}

function main() -> i32 {
    let high: i32 = 150 |> clamp(0, _, 100)
    let low: i32 = -5 |> clamp(0, _, 100)
    let mid: i32 = 42 |> clamp(0, _, 100)
    printf("high=%d low=%d mid=%d\n", high, low, mid)
    return 0
}
```

### 1.4 Chain three stages

```flow
function inc(x: i32) -> i32 { return x + 1 }
function times3(x: i32) -> i32 { return x * 3 }
function dec(x: i32) -> i32 { return x - 1 }

function main() -> i32 {
    let v: i32 = 5 |> inc() |> times3() |> dec()
    printf("%d\n", v)
    return 0
}
```

### 1.5 Pipe into a printer helper

```flow
function label(tag: i32, value: i32) -> i32 {
    printf("tag=%d value=%d\n", tag, value)
    return value
}

function main() -> i32 {
    let v: i32 = 42 |> label(7, _)
    return v - 42
}
```

---

## Part 2: Declarative sort

### 2.1 Sort ints in place (browser)

The browser teaches the *intent*. Native Flow also accepts `xs |> sort` and
`players |> sortBy [desc .score, asc .name]` — see
[`examples/basics/declarative_sort.flow`](../../examples/basics/declarative_sort.flow).

```flow
function main() -> i32 {
    let mut xs: array<i32, 5> = [3, 1, 4, 1, 5]
    # bubble sort in place (browser stand-in for `xs |> sort`)
    for i in 0 to 5 {
        for j in 0 to 4 - i {
            if xs[j] > xs[j + 1] {
                let tmp: i32 = xs[j]
                xs[j] = xs[j + 1]
                xs[j + 1] = tmp
            }
        }
    }
    printf("%d %d %d %d %d\n", xs[0], xs[1], xs[2], xs[3], xs[4])
    return 0
}
```

### 2.2 Descending sort (browser)

```flow
function main() -> i32 {
    let mut xs: array<i32, 5> = [3, 1, 4, 1, 5]
    for i in 0 to 5 {
        for j in 0 to 4 - i {
            if xs[j] < xs[j + 1] {
                let tmp: i32 = xs[j]
                xs[j] = xs[j + 1]
                xs[j + 1] = tmp
            }
        }
    }
    printf("%d .. %d\n", xs[0], xs[4])
    return 0
}
```

### 2.3 Sort by a key field (browser)

```flow
struct Player { score: i32, id: i32 }

function main() -> i32 {
    let mut p: array<Player, 3> = [
        Player { score: 10, id: 2 },
        Player { score: 30, id: 1 },
        Player { score: 20, id: 3 }
    ]
    for i in 0 to 3 {
        for j in 0 to 2 - i {
            if p[j].score < p[j + 1].score {
                let tmp: Player = p[j]
                p[j] = p[j + 1]
                p[j + 1] = tmp
            }
        }
    }
    printf("top=%d id=%d\n", p[0].score, p[0].id)
    return 0
}
```

### 2.4 Native `|> sort` / `sortBy`

```bash
./flow run examples/basics/declarative_sort.flow
./flow run examples/basics/pipeline_placeholder.flow
./flow run examples/basics/pipeline_fork.flow
```

```flow
let mut xs: array<i32, 5> = [3, 1, 4, 1, 5]
xs |> sort
xs |> sort descending

players |> sortBy [desc .score, asc .name]
```

> [!note] Browser vs native
> Full `|> sort` / `sortBy` / fork / choose lower in the native compiler.
> This track's interactive lessons cover `|>` calls and `_`; run the native
> examples for declarative ordering.

---

## Part 3: Chaining fallible work

See [errors.md](errors.md) for Result-shaped pipelines. Native helpers live in
`stdlib/result.flow` (`examples/basics/result_pipeline.flow`).

### 3.1 Map then filter (browser)

```flow
function main() -> i32 {
    let xs: array<i32, 5> = [1, 2, 3, 4, 5]
    let mut sum: i32 = 0
    for i in 0 to 5 {
        let y: i32 = xs[i] * 2
        if y > 5 {
            sum = sum + y
        }
    }
    printf("sum=%d\n", sum)
    return 0
}
```

## Reference

- [Ordering](../language/ordering.md)
- [Language Spec — pipelines](../LANGUAGE_SPEC.md)
