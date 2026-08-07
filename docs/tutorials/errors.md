# Errors & Results

> Return codes and Result-style patterns.


## Part 1: Return codes

### 1.1 Ok vs err

```flow
function div(a: i32, b: i32) -> i32 {
    if b == 0 {
        return -1
    }
    return a / b
}

function main() -> i32 {
    printf("%d\n", div(10, 2))
    printf("%d\n", div(10, 0))
    return 0
}
```
### 1.2 Out-parameter style

```flow
function try_parse(digit: i32, out: ptr<i32>) -> bool {
    if digit < 0 || digit > 9 {
        return false
    }
    out[0] = digit
    return true
}

function main() -> i32 {
    let mut v: i32 = 0
    if try_parse(7, &v) {
        printf("ok %d\n", v)
    }
    if !try_parse(99, &v) {
        printf("err\n")
    }
    return 0
}
```

## Part 2: Result struct

### 2.1 Result_i32

```flow
struct ResultI32 {
    ok: bool,
    value: i32
}

function ok(v: i32) -> ResultI32 {
    return ResultI32 { ok: true, value: v }
}

function err() -> ResultI32 {
    return ResultI32 { ok: false, value: 0 }
}

function main() -> i32 {
    let r: ResultI32 = ok(5)
    if r.ok {
        printf("%d\n", r.value)
    }
    return 0
}
```
### 2.2 Chain with early exit

```flow
struct ResultI32 { ok: bool, value: i32 }

function step(x: i32) -> ResultI32 {
    if x < 0 {
        return ResultI32 { ok: false, value: 0 }
    }
    return ResultI32 { ok: true, value: x + 1 }
}

function main() -> i32 {
    let r1: ResultI32 = step(3)
    if !r1.ok {
        printf("fail\n")
        return 1
    }
    let r2: ResultI32 = step(r1.value)
    printf("%d\n", r2.value)
    return 0
}
```

## Part 3: Assertions

### 3.1 Assertion helper

`expect` is a reserved word in FLOW, so name the helper something else.

```flow
function check(cond: bool, msg: string) -> void {
    if !cond {
        printf("CHECK FAILED: %s\n", msg)
    }
}

function main() -> i32 {
    check(1 + 1 == 2, "math works")
    check(2 + 2 == 5, "this should print")
    return 0
}
```

## Part 4: Result pipelines (native helpers)

Chain fallible steps with `stdlib/result.flow`. Full file:
[`examples/basics/result_pipeline.flow`](../../examples/basics/result_pipeline.flow).

```bash
./flow run examples/basics/result_pipeline.flow
```

### 4.1 Manual Result chain (browser)

Same shape without the stdlib import — early-exit on `ok == false`:

```flow
struct ResultI32 { ok: bool, value: i32 }

function parse_positive(n: i32) -> ResultI32 {
    if n > 0 {
        return ResultI32 { ok: true, value: n }
    }
    return ResultI32 { ok: false, value: 0 }
}

function double_checked(n: i32) -> ResultI32 {
    return ResultI32 { ok: true, value: n * 2 }
}

function clamp_under(n: i32, limit: i32) -> ResultI32 {
    if n > limit {
        return ResultI32 { ok: false, value: 0 }
    }
    return ResultI32 { ok: true, value: n }
}

function pipeline(raw: i32) -> ResultI32 {
    let first: ResultI32 = parse_positive(raw)
    if !first.ok { return first }
    let second: ResultI32 = double_checked(first.value)
    if !second.ok { return second }
    return clamp_under(second.value, 100)
}

function main() -> i32 {
    let r0: ResultI32 = pipeline(20)
    let r1: ResultI32 = pipeline(-3)
    let r2: ResultI32 = pipeline(60)
    let mut ok20: i32 = 0
    let mut fail_neg: i32 = 0
    let mut fail_clamp: i32 = 0
    if r0.ok { ok20 = 1 }
    if !r1.ok { fail_neg = 1 }
    if !r2.ok { fail_clamp = 1 }
    printf("ok20=%d fail_neg=%d fail_clamp=%d\n", ok20, fail_neg, fail_clamp)
    return 0
}
```

### 4.2 unwrap_or

```flow
struct ResultI32 { ok: bool, value: i32 }

function unwrap_or(r: ResultI32, fallback: i32) -> i32 {
    if r.ok {
        return r.value
    }
    return fallback
}

function main() -> i32 {
    let a: ResultI32 = ResultI32 { ok: true, value: 9 }
    let b: ResultI32 = ResultI32 { ok: false, value: 0 }
    printf("%d %d\n", unwrap_or(a, -1), unwrap_or(b, -1))
    return 0
}
```

### 4.3 map on Result

```flow
struct ResultI32 { ok: bool, value: i32 }

function map_double(r: ResultI32) -> ResultI32 {
    if !r.ok {
        return r
    }
    return ResultI32 { ok: true, value: r.value * 2 }
}

function main() -> i32 {
    let a: ResultI32 = map_double(ResultI32 { ok: true, value: 5 })
    let b: ResultI32 = map_double(ResultI32 { ok: false, value: 5 })
    printf("a=%d ok_a=%d ok_b=%d\n", a.value, a.ok, b.ok)
    return 0
}
```

Also see [pipelines.md](pipelines.md) for `|>` and `_`.
