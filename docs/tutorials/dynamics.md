# Flow Tutorial: Dynamics

This tutorial goes from a hand-written integrator to Flow's `flow` and `dsys` surfaces. Every `flow` block is compiler-checked in CI.

## 1. Start with an integrator

```flow
function euler_step(y: f64, dt: f64) -> f64 {
    return y + dt * (0.0 - y)
}

function ten_steps() -> f64 {
    let mut y: f64 = 1.0
    for k in 0 to 10 {
        y = euler_step(y, 0.1)
    }
    return y
}
```

For Euler, midpoint, RK4, and closed-form error comparisons run:

```bash
FLOW_HOST=python ./flow run examples/numerical/ode_solver.flow
```

## 2. Declare the evolution directly

```flow
flow DecayTutorial {
    state amount: f64 = 1.0
    param rate: f64 = 1.0

    amount evolves as -rate * amount
}
```

`flow` separates the model from the numerical stepping policy. See [Evolution](evolution.md) for solvers, periodic updates, and hybrid events.

## 3. State-space systems

Use `dsys` when the model is naturally expressed as `A`, `B`, and `C` matrices:

```flow
dsys tutorial_plant {
    continuous
    dt 0.1
    n 2 m 1 p 1
    A 0.0 1.0 -1.0 -0.2
    B 0.0 1.0
    C 1.0 0.0
}

horizon tutorial_rollout finite 60
```

The compiler expands this into the allocation-free `stdlib/dynamics` implementation and Euler-discretizes the continuous plant for discrete analysis.

## 4. Analyse the plant

Keep the declarations in the same compilation unit as the analysis they support:

```flow
dsys analysed_plant {
    discrete
    dt 0.1
    n 2 m 1 p 1
    A 1.0 0.1 -0.1 0.98
    B 0.0 0.1
    C 1.0 0.0
}

horizon analysed_rollout finite 60

sense on analysed_plant {
    controllable -> plant_ok
    spectral -> rho_open
    gramian finite analysed_rollout trace -> reachability
}
```

`controllable` checks rank; `spectral` reports the spectral radius; the Gramian trace is an energy/reachability measure.

## 5. Search feedback gains

```flow
dsys controlled_plant {
    discrete
    dt 0.1
    n 2 m 1 p 1
    A 1.0 0.1 -0.1 0.98
    B 0.0 0.1
    C 1.0 0.0
}

horizon controlled_rollout finite 60

ga evolve on controlled_plant over controlled_rollout -> k1 k2 {
    population 16
    generations 30
    mutation 0.3
}

closed controlled_plant with k1 k2 {
    spectral -> rho_closed
    energy over controlled_rollout -> closed_energy
    stable -> stable_closed
}
```

The complete model → analyse → control → certify example is:

```bash
FLOW_HOST=python ./flow run examples/evolution/spring_mass_control.flow
```

## 6. LQR

For small linear systems, the shipped LQR path avoids heuristic search:

```flow
dsys lqr_plant {
    continuous
    dt 0.1
    n 2 m 1 p 1
    A 0.0 1.0 -1.0 -0.2
    B 0.0 1.0
    C 1.0 0.0
}

analyze lqr_plant {
    lqr {
        Q 10.0 1.0
        R 0.1
        -> lqr_k1 lqr_k2
    }
}
```

```bash
FLOW_HOST=python ./flow run examples/evolution/spring_mass_lqr.flow
FLOW_HOST=python ./flow run examples/evolution/chain4_lqr.flow
```

## 7. Nonlinear systems

For nonlinear flows use language-level evolution or `stdlib/dynamics/attractor.flow`. The Lorenz examples provide both a numerical and visual validation path:

```bash
FLOW_HOST=python ./flow run examples/dynamics/lorenz_attractor.flow
FLOW_HOST=python ./flow gfx examples/evolution/lorenz_gfx.flow
```

## Next

Continue with [Evolution](evolution.md), the [Dynamics DSL reference](../language/dynamics-dsl.md), the [Dynamics library](../library/dynamics.md), and the [North-star design](../vision/north-star.md).
