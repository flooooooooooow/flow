# Vision

> The canonical, full vision document lives at the repo root: [`VISION.md`](https://github.com/flooooooooooow/flow/blob/main/VISION.md). This page is the one-screen distillation.

Flow is built around **evolution**, not computation. Programs describe how systems evolve through time — as mathematical systems with explicit state, dynamics, timing, constraints, and guarantees — and the compiler turns that description into deterministic, production-ready code.

```text
flow Pendulum {
    angle : Angle
    velocity : AngularVelocity

    angle evolves as velocity
    velocity evolves as
        -(gravity / length) * sin(angle)
}
```

Every Flow program answers five questions:

1. **What exists?** — explicit state, inputs, outputs, parameters
2. **How does it evolve?** — continuous (`evolves as`) and discrete (`becomes`) dynamics
3. **When does it evolve?** — explicit time: `continuous`, `every 1 ms`, `after 50 us`, `within 2 s`
4. **Under what constraints?** — `always { }`, `never { }`
5. **What guarantees must always hold?** — temporal guarantees, realtime bounds, verified at compile time

The goal: replace the fragmented Python → MATLAB → Simulink → C toolchain with one language where **the mathematical model is the executable program** — covering simulation, analysis, control synthesis, verification, and deployment from a single source of truth.

## Where we are

The general-purpose core (types, generics, effects, library autodiff, C/MLIR backends) is shipped, and a seed of the dynamics story exists today: the `dsys` declarative syntax with controllability/spectral/gramian analysis and GA-based control search (see `examples/dynamics/`). The full pillar-by-pillar status table is in [`VISION.md`](https://github.com/flooooooooooow/flow/blob/main/VISION.md#where-flow-is-today); the gaps are tracked on the project board under the **Vision: Evolution** epic.

The core vision constructs are now in the compiler. `flow Name { ... }` blocks with `state` declarations and `x evolves as expr` continuous dynamics parse, type check, and compile to native code: a struct plus a generated `Name_step(self, dt)` that evaluates every derivative from the pre-step state and integrates with explicit Euler. Hybrid events work inside the same blocks: `when height reaches 0.0 { velocity becomes -0.8 * velocity }` fires on zero crossings and applies resets synchronously. Units of measure (`unit Meter`, `unit MeterPerSecond = Meter / Second`) carry dimension vectors through the type checker and erase to plain `f64` at codegen, so dimensional bugs fail at compile time and cost nothing at runtime.

All of it runs on both backends. The same programs execute through the C path (`./flow run`) and the MLIR JIT (`./flow jit`), including the algebraic effects system. Measured performance against hand-written C under identical clang flags is published in `benchmarks/RESULTS.md`. The pendulum from the vision runs today as `examples/evolution/pendulum_evolves.flow`; the bouncing ball as `examples/evolution/bouncing_ball_evolves.flow`. The spec and per-card status live in [docs/vision/north-star.md](vision/north-star.md).
