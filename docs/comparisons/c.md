# Flow vs C

<img src="https://cdn.simpleicons.org/c/A8B9CC" alt="C logo" width="64" height="64">

C is Flow's closest baseline: Flow can lower through portable C, so this comparison is not about escaping C's machine model. It is about how much of that model the programmer should have to spell out.

[← All language comparisons](../comparison.md)

## The short version

C exposes representation and control directly. Flow keeps that escape hatch, but adds language-level ways to describe intent before lowering it to ordinary native code.

The strongest difference is not a shorter `for` loop. It is that a model, effect, or domain operation can be represented directly instead of being reconstructed from structs, helper functions and conventions.

## Example: a dynamical system

Both programs represent the same decay law:

`dx/dt = -rate * x`

### Flow

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

The source says what the state is, what is a parameter, and how the state evolves. Flow generates the state representation and stepping operation.

### C

```c
#include <stdio.h>

typedef struct {
    double value;
    double rate;
} Decay;

static Decay decay_new(void) {
    Decay system = {1.0, 0.5};
    return system;
}

static void decay_step(Decay *system, double dt) {
    double derivative = -system->rate * system->value;
    system->value += derivative * dt;
}

int main(void) {
    Decay system = decay_new();

    for (int i = 0; i < 100; ++i) {
        decay_step(&system, 0.01);
    }

    printf("%f\n", system.value);
    return 0;
}
```

Nothing in the C type system distinguishes state, parameters, evolution law and integration machinery. Those meanings live in names and conventions. Flow preserves them as program structure that the compiler can reason about.

## Example: ordinary systems code stays ordinary

Flow does not force a DSL onto simple code.

```flow
struct Point {
    x: f32,
    y: f32
}

function squared_length(p: Point) -> f32 {
    return p.x * p.x + p.y * p.y
}
```

The equivalent C is already concise:

```c
typedef struct {
    float x;
    float y;
} Point;

float squared_length(Point p) {
    return p.x * p.x + p.y * p.y;
}
```

This is an important boundary. Flow's case is not that every C expression becomes dramatically shorter. The gain appears when semantics that C leaves implicit become first-class language constructs.

## What Flow removes

Flow can remove manually maintained stepping APIs, convention-only domain semantics, repeated plumbing around effects/capabilities, and some target-specific ceremony while retaining explicit structs, pointers, loops, extern declarations and C ABI interoperability when those are actually the right abstraction.

## Where C still wins

Choose C when the ABI itself is the product, when a platform accepts only C, when the environment is so constrained that the smallest possible compiler/runtime surface matters, or when you need the maturity and audit history of a decades-old C codebase.

Flow should beat C by carrying more meaning in the source, not by pretending the machine underneath stopped looking like C.

## See also

[Flow syntax](../language/syntax.md) · [Evolution tutorial](../tutorials/evolution.md) · [C ABI export](../language/export-abi.md) · [Benchmarks](../project/benchmark-results.md)
