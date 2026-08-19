# Appendix A. Language and command card

Use this card for quick recall. The language reference contains the full rules.

## Bindings

```flow
let fixed: i32 = 42
let inferred = 42
let mut changing: f64 = 0.0
changing = changing + 0.5
```

## Functions

```flow
function add(a: i32, b: i32) -> i32 {
    return a + b
}

function notify(message: string) -> void {
    println(message)
}
```

## Control

```text
if condition {
    # ...
} elif other_condition {
    # ...
} else {
    # ...
}

while condition {
    # ...
}

for i in 0 to n {
    # i is in [0, n)
}

for i in 0 to n step 2 {
    # ...
}
```

## Structs and arrays

```flow
struct Point {
    x: f64,
    y: f64
}

let p: Point = Point { x: 1.0, y: 2.0 }
let mut xs: array<i32, 3> = [10, 20, 30]
xs[1] = 25
```

## Pipelines

```text
x |> f              # f(x)
x |> f(y)           # f(x, y)
x |> f(y, _)        # f(y, x)
x |> f() |> g()     # g(f(x))
```

Use the full compiler host for pipelines in the present toolchain.

## Evolution

```flow
flow Model {
    state x: f64 = 1.0
    param rate: f64 = 0.5

    x evolves as 0.0 - rate * x
}
```

## Common commands

```bash
./flow version
./flow run program.flow
./flow compile program.flow
./flow fmt program.flow
./flow test

FLOW_HOST=python ./flow run full_language_program.flow
python3 -m flow.run program.flow --json
```

## References

- [Language specification](../LANGUAGE_SPEC.md)
- [Syntax reference](../language/syntax.md)
- [Type system](../language/types.md)
- [Command runner](../language/flow-run.md)
