# Flow vs Julia

<img src="https://cdn.simpleicons.org/julia/9558B2" alt="Julia logo" width="64" height="64">

Julia is one of the strongest examples of a high-level language that can also deliver serious numerical performance. Flow overlaps with Julia in scientific and simulation work, but it is designed around native systems deployment, explicit low-level control and domain constructs that can lower through C/MLIR-oriented toolchains.

[← All language comparisons](../comparison.md)

## Example: describing evolution

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

### Julia

```julia
mutable struct Decay
    value::Float64
    rate::Float64
end

function step!(system::Decay, dt::Float64)
    derivative = -system.rate * system.value
    system.value += derivative * dt
end

system = Decay(1.0, 0.5)

for _ in 1:100
    step!(system, 0.01)
end

println(system.value)
```

Julia is already very expressive. The Flow difference is that evolution is not merely a convention around a mutable struct and a mutating function. `state`, `param` and `evolves as` are explicit language semantics that can feed analysis, code generation and tooling.

## Where the languages optimize differently

Julia optimizes for interactive numerical programming, multiple dispatch and a deep scientific ecosystem. Flow optimizes for carrying a compact high-level description into deployable systems code without requiring a dynamic runtime as the center of the programming model.

A useful Flow implementation should therefore not merely imitate Julia syntax. It should make simulation, control, DSP and other domains statically meaningful enough that the compiler can lower them directly to the target environment.

## Where Julia still wins

Julia is substantially ahead for scientific packages, differential-equation tooling, optimization, statistics, notebooks, multiple dispatch and exploratory numerical work.

Flow's opportunity is strongest where scientific code must become a small native artifact, cross into real-time or embedded constraints, or live in the same language as lower-level systems and DSP code.

## See also

[Dynamics DSL](../language/dynamics-dsl.md) · [Numerical demos](../demos/numerical.md) · [Autodiff](../library/autodiff.md) · [Evolution tutorial](../tutorials/evolution.md)
