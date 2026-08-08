# Vision

> Full text: [`VISION.md`](https://github.com/flooooooooooow/flow/blob/main/VISION.md) at the repo root. This page is the short version.

Flow is built around evolution, not computation alone. Programs describe how systems change through time: state, dynamics, timing, constraints, and guarantees. The compiler turns that description into deterministic code you can ship.

```flow
flow Pendulum {
    angle : Angle
    velocity : AngularVelocity

    angle evolves as velocity
    velocity evolves as
        -(gravity / length) * sin(angle)
}
```

Every Flow program answers five questions:

1. **What exists?** Explicit state, inputs, outputs, parameters.
2. **How does it evolve?** Continuous (`evolves as`) and discrete (`becomes`) dynamics.
3. **When does it evolve?** Explicit time: `continuous`, `every 1 ms`, `after 50 us`, `within 2 s`.
4. **Under what constraints?** `always { }`, `never { }`.
5. **What must always hold?** Temporal guarantees and realtime bounds, checked at compile time where the toolchain supports them.

The aim is to cut down the Python → MATLAB → Simulink → C hop. One language should cover simulation, analysis, control synthesis, verification, and deployment from the same source.

## Where we are

The general-purpose core (types, generics, effects, library autodiff, C/MLIR backends) is shipped. A seed of the dynamics story is in tree today: `dsys` declarative syntax with controllability, spectral, and Gramian analysis, plus GA-based control search (see `examples/dynamics/`). Pillar-by-pillar status is in [`VISION.md`](https://github.com/flooooooooooow/flow/blob/main/VISION.md#where-flow-is-today); gaps sit on the project board under the **Vision: Evolution** epic.

Core vision constructs are in the compiler. `flow Name { ... }` blocks with `state` and `x evolves as expr` parse, type-check, and compile to native code: a struct plus a generated `Name_step(self, dt)` that evaluates every derivative from the pre-step state and integrates with explicit Euler. Hybrid events work in the same blocks: `when height reaches 0.0 { velocity becomes -0.8 * velocity }` fires on zero crossings and applies resets synchronously. Units of measure (`unit Meter`, `unit MeterPerSecond = Meter / Second`) carry dimension vectors through the type checker and erase to plain `f64` at codegen, so dimensional bugs fail at compile time and cost nothing at runtime.

Both backends run the same programs: C (`./flow run`) and MLIR JIT (`./flow jit`), including algebraic effects. Measured performance against hand-written C under identical clang flags is in `benchmarks/RESULTS.md`. The pendulum from the vision runs as `examples/evolution/pendulum_evolves.flow`; the bouncing ball as `examples/evolution/bouncing_ball_evolves.flow`. Spec and per-card status: [docs/vision/north-star.md](vision/north-star.md).
