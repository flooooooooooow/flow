# Flow in one hour

This is the shortest path from an empty file to understanding what makes Flow different.

## Install

On macOS:

```bash
brew tap flooooooooooow/flow
brew install flow
flow version
```

Or from source:

```bash
git clone https://github.com/flooooooooooow/flow.git
cd flow
./flow version
```

## 1. Run a program

Create `hello.flow`:

```flow
function main() -> i32 {
    println("Hello, Flow!")
    return 0
}
```

Run it:

```bash
flow run hello.flow
```

A conventional Flow program starts at `main() -> i32`.

## 2. Values and mutation

```flow
function main() -> i32 {
    let answer: i32 = 42
    let mut counter: i32 = 0

    counter = counter + 1

    printf("answer = %d\n", answer)
    printf("counter = %d\n", counter)
    return 0
}
```

`let` is immutable. `let mut` is mutable.

## 3. Control flow

```flow
function classify(n: i32) -> void {
    if n > 0 {
        println("positive")
    } elif n < 0 {
        println("negative")
    } else {
        println("zero")
    }
}

function main() -> i32 {
    for i in 0..5 {
        printf("%d\n", i)
    }

    let mut n: i32 = 3
    while n > 0 {
        n = n - 1
    }

    classify(n)
    return 0
}
```

## 4. Functions

```flow
function gcd(a: i32, b: i32) -> i32 {
    let mut x: i32 = a
    let mut y: i32 = b

    while y != 0 {
        let next: i32 = x % y
        x = y
        y = next
    }

    return x
}

function main() -> i32 {
    printf("%d\n", gcd(56, 98))
    return 0
}
```

## 5. Structs

```flow
struct Point {
    x: f64,
    y: f64
}

function length_squared(p: Point) -> f64 {
    return p.x * p.x + p.y * p.y
}

function main() -> i32 {
    let p = Point { x: 3.0, y: 4.0 }
    printf("%.1f\n", length_squared(p))
    return 0
}
```

At this point Flow already feels like a compact compiled systems language. The next part is the reason it exists.

## 6. Model evolution directly

Flow can represent a dynamical system as a first-class program:

```flow
flow Pendulum {
    state angle: f64 = 0.5
    state velocity: f64 = 0.0
    param damping: f64 = 0.3

    angle evolves as velocity
    velocity evolves as -9.81 * sin(angle) - damping * velocity
}
```

Instead of writing a hand-maintained integration loop in one language and translating the model into deployment code later, the evolution equations are part of the program.

The compiler owns the lowering from the model to executable code.

## 7. Use the real examples

The fastest way to learn Flow is to run programs that already exercise a complete domain:

```bash
./flow run examples/basics/fibonacci.flow
./flow run examples/ml/models/mlp_xor.flow
./flow run examples/audio/rt_safe_callback.flow
./flow gfx examples/games/tetris_gfx.flow
./flow gfx examples/morphogenesis/gray_scott.flow
./flow gfx examples/neuro/hodgkin_huxley.flow
```

Use `examples/STATUS.md` to see machine-generated compile status across the example corpus.

## 8. Learn the toolchain

```bash
./flow run program.flow
./flow compile program.flow
./flow fmt program.flow
./flow repl
./flow lsp
./flow test
./flow gfx program.flow
./flow mlir program.flow
```

The default production path is the self-hosted compiler targeting portable C. Advanced language and backend surfaces can still require the Python host; the repository documents those boundaries explicitly.

## 9. Where to go next

For ordinary language work, continue with [beginner](beginner.md), [functions](functions.md), [arrays](arrays.md), [memory](memory.md), and [systems](systems.md).

For Flow's distinctive domain model, continue with [evolution](evolution.md), [dynamics](dynamics.md), [audio](audio-basics.md), [real-time audio](rt-audio.md), [autodiff](autodiff-basics.md), and [graphics](gfx-basics.md).

For the exact language contract, use the [language specification](../LANGUAGE_SPEC.md).

The key idea to retain is simple: ordinary code describes computation; Flow can also describe how a system evolves through time, and compile that description directly.
