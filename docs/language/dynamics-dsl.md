# Dynamics DSL (`dsys`)

Flow ships a declarative surface for linear dynamical systems: declare a plant, choose an analysis horizon, measure controllability and stability, evolve feedback gains, and certify the closed loop.

The DSL is expanded before the core parser by `src/flow/dynamics_dsl.py`. Every `flow` block on this page is compiler-checked in CI and is self-contained rather than relying on declarations from an earlier fence.

The command-line entry point is `flow analyze`. Larger working examples are [`examples/dynamics/ga_dsys_syntax.flow`](../../examples/dynamics/ga_dsys_syntax.flow) and [`examples/evolution/spring_mass_control.flow`](../../examples/evolution/spring_mass_control.flow).

## Current envelope

The shipped GA analysis path targets 2-state, single-input, single-output systems (`n 2 m 1 p 1`). Continuous declarations are Euler-discretized before analysis. Keep GA `generations` at 32 or below because the convergence-history buffer is sized for 32 entries.

## Declare a system

```flow
dsys plant {
    discrete
    dt 0.1
    n 2 m 1 p 1
    A 1.0 0.1 0.0 1.0
    B 0.0 0.1
    C 1.0 0.0
}
```

`A`, `B`, and `C` are row-major flat matrices. `continuous` may replace `discrete`; the expander then forms `Ad = I + dt*A` and `Bd = dt*B` for the analysis path.

## Horizons and open-loop analysis

A `sense` block references a declared plant and horizon, so this example includes both:

```flow
dsys sense_plant {
    discrete
    dt 0.1
    n 2 m 1 p 1
    A 1.0 0.1 0.0 1.0
    B 0.0 0.1
    C 1.0 0.0
}

horizon sense_rollout finite 50
horizon sense_asymptotic infinite gamma 0.99

sense on sense_plant {
    controllable -> plant_ok
    spectral -> rho_open
    gramian finite sense_rollout trace -> wc_fin
    gramian infinite sense_asymptotic trace -> wc_inf
}
```

The bindings created by `sense` become ordinary locals in the generated `main` setup.

## Evolving feedback gains

```flow
dsys ga_plant {
    discrete
    dt 0.1
    n 2 m 1 p 1
    A 1.0 0.1 0.0 1.0
    B 0.0 0.1
    C 1.0 0.0
}

horizon ga_rollout finite 50

ga evolve on ga_plant over ga_rollout -> k1 k2 {
    population 12
    generations 30
    mutation 0.3
}
```

The GA minimizes the shipped quadratic rollout objective and binds the best state-feedback gains to `k1` and `k2`.

## Closed-loop certification

```flow
dsys closed_plant {
    discrete
    dt 0.1
    n 2 m 1 p 1
    A 1.0 0.1 0.0 1.0
    B 0.0 0.1
    C 1.0 0.0
}

horizon closed_rollout finite 50

ga evolve on closed_plant over closed_rollout -> ck1 ck2 {
    population 8
    generations 10
    mutation 0.3
}

closed closed_plant with ck1 ck2 {
    spectral -> rho_cl
    energy over closed_rollout -> energy_cl
    stable -> stable_cl
}
```

The closed-loop matrix is `A - B*K`. `stable` binds an integer flag indicating whether its spectral radius is below one.

## Unified analysis report

```flow
dsys report_plant {
    discrete
    dt 0.1
    n 2 m 1 p 1
    A 1.0 0.1 0.0 1.0
    B 0.0 0.1
    C 1.0 0.0
}

horizon report_rollout finite 50

analyze report_plant ga rk1 rk2 over report_rollout -> report {
    full
}
```

The report includes baseline cost, evolved gains, controllability, open- and closed-loop spectral radii, Gramian traces, closed-loop energy, and convergence information.

## Complete runnable example

```flow
extern {
    function printf(fmt: string, val: f64) -> i32
}

dsys demo_plant {
    discrete
    dt 0.1
    n 2 m 1 p 1
    A 1.0 0.1 0.0 1.0
    B 0.0 0.1
    C 1.0 0.0
}

horizon demo_rollout finite 50

sense on demo_plant {
    controllable -> demo_ok
    spectral -> demo_rho_open
}

ga evolve on demo_plant over demo_rollout -> demo_k1 demo_k2 {
    population 12
    generations 30
    mutation 0.3
}

closed demo_plant with demo_k1 demo_k2 {
    spectral -> demo_rho_closed
    stable -> demo_stable
}

function main() -> i32 {
    printf("%.4f", demo_rho_open)
    printf("%.4f", demo_rho_closed)
    return 0
}
```

Run a checked-in version with:

```bash
FLOW_HOST=python ./flow run examples/dynamics/ga_dsys_syntax.flow
```

## Namespaced spelling

`dyn.` / `dynamics.` prefixes and `dynamics { ... }` are supported conveniences around the same DSL. The checked-in example [`examples/dynamics/ga_dsys_namespaced.flow`](../../examples/dynamics/ga_dsys_namespaced.flow) is the source of truth for that surface.

## WFC coupling

The expander also supports the experimental WFC coupling blocks used by [`examples/dynamics/ga_wfc_coupled.flow`](../../examples/dynamics/ga_wfc_coupled.flow). Because those blocks are easiest to understand as one complete program, the reference links to the executable example instead of presenting disconnected partial fences.

## Relationship to `flow` evolution

`dsys` is the shipped matrix-oriented analysis surface. First-class `flow Name { ... }` declarations are the newer language-level model for state, parameters, `evolves as`, hybrid `when ... reaches ...` events, and periodic `every` blocks. See [Evolution and dynamics](../book/13-evolution-and-dynamics.md) and [North-star](../vision/north-star.md).

Automatic Jacobian linearization, richer pole-analysis syntax, multi-rate composition, and some north-star control constructs remain future work. Those appear only in explicitly labelled `flow-future` blocks, never as current runnable Flow.
