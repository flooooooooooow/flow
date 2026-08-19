# 6. Pipelines and explicit results

Run the examples with the Python compiler host:

```bash
FLOW_HOST=python ./flow run file.flow
```

## 6.1 Forward composition

The pipeline operator sends a value into a function call:

```flow
x |> f
x |> f()
x |> f(y)
```

They compile as:

```flow
f(x)
f(x)
f(x, y)
```

A chain is evaluated from left to right:

```flow
let result: i32 = 5 |> increment() |> double()
```

is equivalent to:

```flow
let result: i32 = double(increment(5))
```

A pipeline changes the notation, not the order of evaluation. It reads well
when a value passes through several functions in sequence.

## 6.2 Argument placement

By default, the piped value becomes the first argument. A single `_`
placeholder selects a different position:

```flow
function clamp(lo: i32, value: i32, hi: i32) -> i32 {
    if value < lo { return lo }
    if value > hi { return hi }
    return value
}

let bounded: i32 = raw |> clamp(0, _, 100)
```

It compiles as:

```flow
let bounded: i32 = clamp(0, raw, 100)
```

Exactly one pipeline value enters each stage. More than one `_` in a stage is
rejected because it would duplicate that value implicitly.

## 6.3 Failure as data

A return code can report failure for an entire process. A reusable function
needs a value-level representation:

```flow
struct ResultI32 {
    ok: bool,
    value: i32
}
```

A validator constructs either state explicitly:

```flow
function parse_port(raw: i32) -> ResultI32 {
    if raw < 1 or raw > 65535 {
        return ResultI32 { ok: false, value: 0 }
    }
    return ResultI32 { ok: true, value: raw }
}
```

The caller must inspect `ok` before using `value`. Failure is therefore part
of the result type instead of an unstated convention.

## 6.4 Complete demonstration

```flow from=examples/book/06_pipeline_result.flow
extern {
    function printf(fmt: string, ...) -> i32
}

struct ResultI32 {
    ok: bool,
    value: i32
}

function parse_port(raw: i32) -> ResultI32 {
    if raw < 1 or raw > 65535 {
        return ResultI32 { ok: false, value: 0 }
    }
    return ResultI32 { ok: true, value: raw }
}

function add(a: i32, b: i32) -> i32 {
    return a + b
}

function clamp(lo: i32, value: i32, hi: i32) -> i32 {
    if value < lo { return lo }
    if value > hi { return hi }
    return value
}

function main() -> i32 {
    let adjusted: i32 = 8080 |> add(10) |> clamp(1, _, 65535)
    let valid: ResultI32 = parse_port(adjusted)
    let invalid: ResultI32 = parse_port(70000)

    printf("adjusted: %d\n", adjusted)
    printf("valid: %d invalid: %d\n", valid.ok, invalid.ok)

    if !valid.ok or invalid.ok {
        return 1
    }
    return 0
}
```

Source:
[`examples/book/06_pipeline_result.flow`](../../examples/book/06_pipeline_result.flow)

```bash
FLOW_HOST=python ./flow run examples/book/06_pipeline_result.flow
```

```text
adjusted: 8090
valid: 1 invalid: 0
```

## 6.5 Chaining fallible operations

When each stage can fail, test the result before continuing:

```flow
function configure(raw: i32) -> ResultI32 {
    let port: ResultI32 = parse_port(raw)
    if !port.ok {
        return port
    }

    let adjusted: i32 = port.value |> add(10)
    return parse_port(adjusted)
}
```

The checks are explicit. A failed value cannot reach the next operation.

## Exercises

1. Add `error_code: i32` to `ResultI32`.
2. Write `unwrap_or(result, fallback)`.
3. Construct a three-stage numeric pipeline and then write the equivalent
   nested expression.
4. Write a function that doubles a valid port and returns failure if the
   result exceeds `65535`.

Next: [From update loops to flows](07-from-updates-to-flows.md).
