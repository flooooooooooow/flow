# Flow vs Mojo

<div style="font-size:64px" aria-label="Mojo flame logo">🔥</div>

Mojo and Flow both want high-level code to survive all the way down to fast native execution. Mojo approaches that problem from Python, metaprogramming and accelerator kernels. Flow approaches it from systems programming, effects, domain-specific semantics and portable lowering.

[← All language comparisons](../comparison.md)

## The short version

Mojo is a direct competitor for performance-sensitive AI and numerical work. Flow's strongest differentiator is not “Python syntax but faster”; it is making concepts such as effects, evolution, DSP and target behavior part of the language rather than expecting libraries to provide all of the semantic structure.

## Example: a model as a declaration

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

### Mojo

```mojo
struct Decay:
    var value: Float64
    var rate: Float64

    fn __init__(out self):
        self.value = 1.0
        self.rate = 0.5

    fn step(mut self, dt: Float64):
        var derivative = -self.rate * self.value
        self.value += derivative * dt

fn main():
    var system = Decay()

    for _ in range(100):
        system.step(0.01)

    print(system.value)
```

The Mojo implementation is readable and close to Python. Flow encodes an additional layer of meaning: the compiler sees state, parameters and the evolution law as such, not merely as fields and a method.

## Different kinds of expressiveness

Mojo's expressiveness is especially strong in compile-time metaprogramming, SIMD/GPU kernels, parameterization and Python-adjacent numerical code. Flow's intended advantage is semantic compression across a broader systems program: effects and capabilities, dynamics, audio/DSP surfaces, native interop and multiple lowering targets can share one language model.

That means a useful Flow-vs-Mojo comparison should eventually include complete kernels and applications, not syntax screenshots. This page deliberately avoids performance claims that are not backed by equivalent measurements.

## Where Mojo still wins

Mojo is the stronger choice today when the center of gravity is MAX, accelerator kernels, Python-adjacent AI infrastructure or Mojo's mature compile-time GPU programming model.

Flow's case becomes stronger when the application mixes systems code, real-time constraints, DSP, simulation, effects and domain models and you want those ideas to remain visible in one source language.

## Version note

This page targets the Mojo 1.0-era language surface. Mojo changes quickly, so examples should be kept aligned with the current [Mojo documentation](https://mojolang.org/docs/).

## See also

[ML on MacBook](../tutorials/ml-on-macbook.md) · [Shaders](../language/shaders.md) · [Effects showcase](../effects-showcase.md) · [Autodiff](../library/autodiff.md)
