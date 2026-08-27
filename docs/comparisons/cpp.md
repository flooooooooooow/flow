# Flow vs C++

<img src="https://cdn.simpleicons.org/cplusplus/00599C" alt="C++ logo" width="64" height="64">

C++ can express almost anything Flow can ultimately execute, but it often asks the programmer to assemble that meaning from classes, templates, libraries and conventions. Flow's design goal is to make common high-performance patterns read like the thing being built rather than the machinery used to build it.

[← All language comparisons](../comparison.md)

## The short version

C++ is more mature and vastly broader today. Flow aims for a smaller surface where domain meaning can be encoded directly without giving up native compilation or explicit control.

## Example: the model is the program

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

### C++

```cpp
#include <iostream>

struct Decay {
    double value = 1.0;
    double rate = 0.5;

    void step(double dt)
    {
        const double derivative = -rate * value;
        value += derivative * dt;
    }
};

int main()
{
    Decay system;

    for (int i = 0; i < 100; ++i)
        system.step(0.01);

    std::cout << system.value << '\n';
}
```

The C++ is perfectly reasonable, but `value` and `rate` are just fields and `step` is just a method. Flow preserves the distinctions between state, parameter and evolution law in the syntax itself. That gives later compiler passes something stronger than naming conventions to work with.

## Example: plain data stays plain

### Flow

```flow
struct Point {
    x: f32,
    y: f32
}

function squared_length(p: Point) -> f32 {
    return p.x * p.x + p.y * p.y
}
```

### C++

```cpp
struct Point {
    float x;
    float y;
};

float squared_length(Point p)
{
    return p.x * p.x + p.y * p.y;
}
```

Flow is not trying to manufacture a syntax win where C++ is already direct. Its expressiveness advantage is intended to appear at the abstraction boundaries where C++ usually grows framework code.

## The deeper difference

In C++, a project commonly develops its own vocabulary through templates, RAII wrappers, callback types, expression templates, concepts, allocators and framework-specific macros. That can be extraordinarily powerful, but the resulting language is partly C++ and partly the framework.

Flow tries to move recurring high-value concepts into the language itself: effects and capabilities, evolution and dynamics, explicit target surfaces, structured concurrency paths, audio/DSP-oriented primitives and compile-time lowering to portable native code.

The intended payoff is less local metaprogramming and less framework-specific glue for code that should be obvious to a reader who knows Flow.

## Where C++ still wins

C++ wins today on ecosystem depth, vendor SDK support, mature debuggers and profilers, template metaprogramming breadth, standard-library coverage, game engines, GUI frameworks, embedded vendor support and the sheer amount of production code already written in it.

Flow's bar is therefore not merely “fewer characters than C++.” It is whether a complete system can carry the same intent with fewer user-defined abstractions and less incidental machinery.

## See also

[Language overview](../language/overview.md) · [Effects showcase](../effects-showcase.md) · [Evolution tutorial](../tutorials/evolution.md) · [C interop](../language/export-abi.md)
