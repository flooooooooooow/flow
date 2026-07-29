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

### 3.1 Expect helper

```flow
function expect(cond: bool, msg: string) -> void {
    if !cond {
        printf("EXPECT: %s\n", msg)
    }
}

function main() -> i32 {
    expect(1 + 1 == 2, "math works")
    expect(2 + 2 == 5, "this should print")
    return 0
}
```
