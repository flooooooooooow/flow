# Vision

> The canonical, full vision document lives at the repo root: [`VISION.md`](https://github.com/flooooooooooow/flow/blob/main/VISION.md). This page is the one-screen distillation.

Flow is built around **evolution** rather than computation. Programs describe how systems evolve through time, as mathematical systems with explicit state, dynamics, timing, constraints, and guarantees, and the compiler turns that description into deterministic, production-ready code.

```flow-future
flow Pendulum {
    angle : Angle
    velocity : AngularVelocity

    angle evolves as velocity
    velocity evolves as
        -(gravity / length) * sin(angle)
}
```

Every Flow program answers five questions:

1. **What exists?** Explicit state, inputs, outputs, parameters
2. **How does it evolve?** Continuous (`evolves as`) and discrete (`becomes`) dynamics
3. **When does it evolve?** Explicit time: `continuous`, `every 1 ms`, `after 50 us`, `within 2 s`
4. **Under what constraints?** `always { }`, `never { }`
5. **What guarantees must always hold?** Temporal guarantees, realtime bounds, verified at compile time

The goal: replace the fragmented Python → MATLAB → Simulink → C toolchain with one language where **the mathematical model is the executable program**, covering simulation, analysis, control synthesis, verification, and deployment from a single source of truth.

## Where Flow Is Today

| Vision pillar | Status today |
|---|---|
| General-purpose core (functions, generics, ADTs, pattern matching, traits) | **Shipped**: statically-typed language compiling to C via self-hosted `flowc` and `./flow` |
| Dynamical systems | **Shipped**: `flow` blocks with continuous dynamics (`x evolves as expr`), explicit `solver { dt ... method ... }`, Euler and RK4 codegen; linear systems in `dsys` |
| Analysis (controllability, spectral, gramians) | **Shipped**: `sense on <plant>` blocks over `dsys` systems and synthesized `<Flow>_lin` from `represent linear` |
| Control synthesis | **Shipped**: GA-based gain search over rollout horizons (`ga evolve on`), discrete LQR via `analyze { lqr }` |
| Automatic differentiation | **Shipped**: native forward and reverse mode autodiff |
| Algebraic effects | **Shipped**: effect declarations, capability requirements, and `handle ... with` handlers |
| `evolves as` continuous dynamics, ODE solvers as codegen | **Shipped**: `flow` blocks lower simultaneously to pure derivative functions and step integrators (`examples/evolution/pendulum_evolves.flow`) |
| Units in the type system / dimensional analysis | **Shipped**: `unit` declarations, dimension exponent vectors, compile-time arithmetic checking, SI units in `lib/stdlib/units_si.flow` (`examples/evolution/units_kinematics.flow`) |
| Explicit time (`every 1 ms`, durations) | **Shipped**: duration literals (`ns`, `us`, `ms`, `s`, `min`), periodic discrete blocks (`every <duration> { x becomes expr }`) with accumulators and catch-up loops |
| Hybrid events (`when x reaches 0 { x becomes ... }`) | **Shipped**: zero-crossing event guards with synchronous state resets (`examples/evolution/bouncing_ball_evolves.flow`) |
| `always` / `never` / temporal guarantees | **Shipped**: state invariant blocks (`always { ... }`, `never { ... }`) checked on every step with panic on violation (`examples/evolution/pendulum_always.flow`) |
| Flow composition (`connect { a.out -> b.in }`) | **Shipped**: composite flows with member wiring (`connect`), parent-to-child input routing, and pipeline stages via `\|>` (`examples/evolution/parent_input_connect.flow`) |
| Representations (linear, Koopman, transfer function) | **Seed shipped**: `represent linear` blocks with equilibrium linearization synthesized into `dsys` (`examples/evolution/pendulum_represent_linear.flow`); Koopman and transfer functions remain research epics |
| Realtime memory model, deployment blocks, fixed-point numerics | **Shipped (Realtime & Numerics)**: `@rt_safe` compile-time verification prohibiting heap allocations; `Q16_16` and `Q8_24` fixed-point types, saturating arithmetic, MMIO, bitfields; deployment partitions on Flow 3.0 roadmap |

Both backends execute these models. The same programs execute through the C path (`./flow run`) and the MLIR JIT (`./flow jit`), including algebraic effects. Measured performance against hand-written C under identical clang flags is published in `benchmarks/RESULTS.md`. The pendulum from the vision runs today as `examples/evolution/pendulum_evolves.flow`; the bouncing ball as `examples/evolution/bouncing_ball_evolves.flow`. The specification and per-card status live in [docs/vision/north-star.md](vision/north-star.md).
