# 9. Expressions, matching, and declarative operations

An expression produces a value. A statement changes control or program state. Every `flow` block in this chapter is compiler-checked in CI.

## 9.1 Operators

Flow supports arithmetic, comparison, logical, and integer bit operators:

```flow
function permission_bits() -> i32 {
    let read: i32 = 1
    let write: i32 = 2
    let execute: i32 = 4
    let permissions: i32 = read | write
    let can_write: bool = (permissions & write) != 0
    let shifted: i32 = execute << 3
    let toggled: i32 = permissions ^ write
    let inverted: i32 = ~permissions
    if can_write and inverted != 0 {
        return shifted + toggled
    }
    return 0
}
```

## 9.2 Value-producing `if`

```flow
function magnitude(n: i32) -> i32 {
    let value: i32 = if n >= 0 { n } else { -n }
    return value
}
```

Both arms must produce compatible types and an `else` arm is required.

## 9.3 Closures

```flow
function apply(f: (i32) -> i32, x: i32) -> i32 {
    return f(x)
}

function make_adder(n: i32) -> (i32) -> i32 {
    return |x: i32| -> i32 { return x + n }
}

function closure_result() -> i32 {
    let add5: (i32) -> i32 = make_adder(5)
    return apply(add5, 37)
}
```

Free variables are captured by value at closure creation. The C backend supports capturing closures; MLIR support remains narrower.

## 9.4 Match arms

```flow
function bucket(n: i32) -> string {
    match n {
        0 => { return "zero" }
        1 | 2 | 3 => { return "small" }
        x if x < 0 => { return "negative" }
        default { return "other" }
    }
}
```

Arms are tested in source order. Guards may fall through; `_`/bindings and structured patterns are supported.

Struct patterns destructure fields positionally:

```flow
struct MatchPoint {
    x: i32,
    y: i32
}

function point_sum(point: MatchPoint) -> i32 {
    match point {
        MatchPoint(0, 0) => { return 0 }
        MatchPoint(x, y) => { return x + y }
    }
    return -1
}
```

Fixed arrays support list patterns:

```flow
function tail_sum(samples: array<i32, 3>) -> i32 {
    match samples {
        [0, second, third] => { return second + third }
        default { return 0 }
    }
}
```

See [`tests/lang/test_match_patterns.flow`](../../tests/lang/test_match_patterns.flow) for the complete backend test surface.

## 9.5 Loop exits

```flow
function first_multiple_of_seven(limit: i32) -> i32 {
    let mut answer: i32 = -1
    let mut n: i32 = 1
    while n < limit {
        if n % 2 == 0 {
            n = n + 1
            continue
        }
        if n % 7 == 0 {
            answer = n
            break
        }
        n = n + 1
    }
    return answer
}
```

`continue` starts the next iteration and `break` exits the nearest loop.

## 9.6 Deferred cleanup

```flow
extern {
    function malloc(size: i64) -> ptr<void>
    function free(p: ptr<void>) -> void
}

function allocate_then_release() -> i32 {
    let buffer: ptr<void> = malloc(1024)
    if buffer == null { return 1 }
    defer free(buffer)
    return 0
}
```

Deferred actions run when control leaves the scope, including through early return, in reverse declaration order.

## 9.7 Data-parallel loops

```flow
function scale(input: ptr<f32>, output: ptr<f32>, n: i32) -> void {
    parallel for i in 0 to n {
        output[i] = input[i] * 2.0
    }
}
```

The C backend emits OpenMP when available and a serial loop otherwise. Parallel iterations must not race on shared mutable state.

## 9.8 Declarative ordering and search

Flow supports declarative `sort`, `sortBy`, `unique`, and `find` pipelines. These forms are best learned from complete executable programs rather than disconnected snippets:

[`examples/basics/declarative_sort.flow`](../../examples/basics/declarative_sort.flow) can be inspected with:

```bash
FLOW_HOST=python ./flow explain examples/basics/declarative_sort.flow
```

## 9.9 Fork and choose pipelines

Fork and `choose` are also documented through complete checked-in programs so every surrounding type is visible:

```bash
FLOW_HOST=python ./flow run examples/basics/pipeline_fork.flow
FLOW_HOST=python ./flow run examples/basics/pipeline_fork_inferred.flow
FLOW_HOST=python ./flow run examples/basics/pipeline_choose.flow
```

## Exercises

Pack Boolean settings into an integer; classify values with a guarded match; write a closure capturing two coefficients; and compare plans selected by `flow explain` for different data shapes.

Next: [Memory, spans, and lifetime domains](10-memory-and-lifetimes.md).
