# 6. Pipelines and explicit results

Run full-language examples with the Python compiler host:

```bash
FLOW_HOST=python ./flow run file.flow
```

Every `flow` block below is compiler-checked in CI.

## 6.1 Forward composition

The pipeline operator sends the value on its left into the call on its right:

```flow
function increment(x: i32) -> i32 { return x + 1 }
function double(x: i32) -> i32 { return x * 2 }

function pipeline_value() -> i32 {
    return 5 |> increment() |> double()
}
```

That is equivalent to `double(increment(5))`. A pipeline changes notation, not evaluation order.

## 6.2 Argument placement

By default the piped value becomes the first argument. A single `_` placeholder selects another position:

```flow
function clamp(lo: i32, value: i32, hi: i32) -> i32 {
    if value < lo { return lo }
    if value > hi { return hi }
    return value
}

function bounded(raw: i32) -> i32 {
    return raw |> clamp(0, _, 100)
}
```

`raw |> clamp(0, _, 100)` is equivalent to `clamp(0, raw, 100)`. More than one `_` in a stage is rejected because it would duplicate the piped value implicitly.

## 6.3 Failure as data

A reusable function can return an explicit result struct:

```flow
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
```

The caller checks `ok` before using `value`, so failure is represented in data rather than an unstated convention.

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

Source: [`examples/book/06_pipeline_result.flow`](../../examples/book/06_pipeline_result.flow)

```bash
FLOW_HOST=python ./flow run examples/book/06_pipeline_result.flow
```

## 6.5 Chaining fallible operations

When each stage can fail, inspect the result before continuing:

```flow
struct ConfigureResult {
    ok: bool,
    value: i32
}

function parse_config_port(raw: i32) -> ConfigureResult {
    if raw < 1 or raw > 65535 {
        return ConfigureResult { ok: false, value: 0 }
    }
    return ConfigureResult { ok: true, value: raw }
}

function add_ten(value: i32) -> i32 {
    return value + 10
}

function configure(raw: i32) -> ConfigureResult {
    let port: ConfigureResult = parse_config_port(raw)
    if not port.ok {
        return port
    }

    let adjusted: i32 = port.value |> add_ten()
    return parse_config_port(adjusted)
}
```

The failed value never reaches the next operation.

## Exercises

Add `error_code: i32` to the result struct; write `unwrap_or`; construct a three-stage numeric pipeline and its equivalent nested expression; then write a checked port-doubling function.

Next: [From update loops to flows](07-from-updates-to-flows.md).
