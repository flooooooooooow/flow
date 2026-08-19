# Flow Quickstart

Get from installation to a real Flow program in a few minutes. Every fenced block labelled `flow` on this page is compiled in CI; none of the examples depend on hidden code or omitted declarations.

## 1. Install Flow

### Homebrew

```bash
brew tap flooooooooooow/flow
brew install flow
flow version
```

### From source

```bash
git clone https://github.com/flooooooooooow/flow.git
cd flow
./flow version
```

Requirements are Clang or GCC and Python 3.9+ for the full compiler host. `flow run` and `flow compile` default to the self-hosted Stage-A `flowc`; the examples below use `FLOW_HOST=python` because they intentionally exercise the full language surface, including `println` and `flow` evolution blocks.

If you installed from source, replace `flow` with `./flow` in the commands below.

## 2. Hello, Flow

Create `hello.flow`:

```flow
function main() -> i32 {
    println("Hello, Flow!")
    return 0
}
```

Run it:

```bash
FLOW_HOST=python flow run hello.flow
```

You now have a Flow source file compiled through the Flow frontend, emitted as C, compiled to a native executable, and run.

## 3. Variables, control flow, and loops

Create `basics.flow`:

```flow
function main() -> i32 {
    let x: i32 = 42
    let mut total: i32 = 0

    if x > 0 {
        println("positive")
    } else {
        println("not positive")
    }

    for i in 0 to 10 {
        total = total + i
    }

    let mut countdown: i32 = 3
    while countdown > 0 {
        countdown = countdown - 1
    }

    println(total)
    return 0
}
```

```bash
FLOW_HOST=python flow run basics.flow
```

## 4. Functions and structs

Create `point.flow`:

```flow
struct Point {
    x: f32,
    y: f32
}

function squared_length(p: Point) -> f32 {
    return p.x * p.x + p.y * p.y
}

function main() -> i32 {
    let p: Point = Point { x: 3.0, y: 4.0 }
    println(squared_length(p))
    return 0
}
```

```bash
FLOW_HOST=python flow run point.flow
```

## 5. The Flow part: describe evolution directly

Create `decay.flow`:

```flow
flow Decay {
    state value : f64 = 1.0
    param rate  : f64 = 0.5

    value evolves as -rate * value
}

function main() -> i32 {
    let mut system: Decay = Decay_new()

    for i in 0 to 100 {
        Decay_step(&system, 0.01)
    }

    println(system.value)
    return 0
}
```

```bash
FLOW_HOST=python flow run decay.flow
```

The `flow` declaration is the model. The compiler generates the state representation and `Decay_step`; your program only decides when to advance it.

For a larger shipped example:

```bash
FLOW_HOST=python flow run examples/evolution/pendulum_evolves.flow
```

## 6. Useful commands

```bash
flow version
FLOW_HOST=python flow run file.flow
FLOW_HOST=python flow compile file.flow
FLOW_HOST=python flow test
flow fmt file.flow
```

The self-hosted Stage-A subset can be exercised directly with plain `flow run` / `flow compile`. See [self-hosting](project/self-hosting.md) for the current boundary between Stage-A and the full Python-host compiler.

## 7. Next steps

| Goal | Resource |
|------|----------|
| Learn the language progressively | [Beginner tutorial](tutorials/beginner.md) |
| See the language surface | [Language reference](LANGUAGE_SPEC.md) |
| Algebraic effects and capabilities | [Effects showcase](effects-showcase.md) |
| Evolution and dynamical systems | [Evolution tutorial](tutorials/evolution.md) |
| Examples by domain | [Examples index](../examples/README.md) |
| Full project vision | [Vision](../VISION.md) |

New to programming entirely? [Start here](start-here.md) gives a slower terminal-first walkthrough.

## Troubleshooting

If `flow` is not found after a source checkout, use `./flow`. If Clang/GCC is missing, install Xcode Command Line Tools on macOS with `xcode-select --install`, or `build-essential` on Debian/Ubuntu.

If a full-language example reports a Stage-A subset error, make sure the command begins with `FLOW_HOST=python`.