# Dynamics Library

`lib/stdlib/dynamics/` contains the low-level allocation-free implementation behind Flow's dynamics DSL. Matrices wrap caller-provided buffers; analyses accept explicit scratch storage. For most application code, prefer the compiler-checked [`dsys` surface](../language/dynamics-dsl.md), which generates that boilerplate.

## Modules

| Module | Main responsibility |
|---|---|
| `linalg.flow` | `Matrix`, matrix/vector operations |
| `core.flow` | `DynamicalSystem`, `Horizon`, state-space constructors |
| `state_space.flow` | stepping, rollout, controllability |
| `gramian.flow` | controllability/observability Gramians |
| `attractor.flow` | nonlinear vector fields, RK4, Lyapunov proxy |
| `ga.flow` | genetic search for two-state feedback gains |
| `ga_analysis.flow` | unified GA/control report |
| `wfc.flow` | Wave Function Collapse grid operations |
| `wfc_ga_coupling.flow` | GA-guided WFC coupling |

The source files are the authoritative signatures. This page deliberately does not copy isolated calls that omit their imported `Matrix`, `DynamicalSystem`, `GAConfig`, or scratch-buffer context.

## Recommended executable surface

A complete system declaration compiles as written:

```flow
dsys reference_plant {
    discrete
    dt 0.1
    n 2 m 1 p 1
    A 1.0 0.1 0.0 1.0
    B 0.0 0.1
    C 1.0 0.0
}

horizon reference_rollout finite 50

sense on reference_plant {
    controllable -> reference_ok
    spectral -> reference_radius
    gramian finite reference_rollout trace -> reference_gramian
}
```

The DSL expands into the same low-level library calls described below.

## Linear algebra

`Matrix` is a row-major dense `f64` view over caller-owned storage. Important operations include `matrix_zeros`, `matrix_identity`, `matrix_get`, `matrix_set`, `matrix_copy`, `matrix_add`, `matrix_sub`, `matrix_scale`, `matrix_mul`, `matrix_transpose`, `matrix_trace`, `matvec`, `vec_copy`, `vec_scale`, `vec_add`, `vec_dot`, and `vec_norm`.

```bash
FLOW_HOST=python ./flow run examples/dynamics/controllability_demo.flow
FLOW_HOST=python ./flow run examples/dynamics/gramian_demo.flow
```

## State-space systems

`core.flow` defines discrete/continuous `DynamicalSystem` values and finite/infinite `Horizon` values. `state_space.flow` provides discrete stepping, Euler stepping for continuous models, rollout, controllability matrices, rank estimation, and similarity transforms.

## Gramians

`gramian_finite_horizon` and `observability_gramian_finite` accumulate finite-horizon energy matrices. `gramian_infinite_horizon` performs the shipped discounted fixed-point Lyapunov iteration. The DSL's `sense ... gramian ... trace` form is the high-level interface.

## Nonlinear attractors

`attractor.flow` contains built-in vector fields plus `rk4_step_n`, `integrate_attractor`, and `lyapunov_proxy`.

```bash
FLOW_HOST=python ./flow run examples/dynamics/lorenz_attractor.flow
FLOW_HOST=python ./flow gfx examples/evolution/lorenz_gfx.flow
```

## Genetic controller search

`ga.flow` searches two state-feedback gains `u = -k1*x1 - k2*x2`. `ga_analysis.flow` adds controllability, spectral-radius, Gramian, closed-loop energy, cost, convergence, and stability reporting.

```flow
dsys ga_reference {
    discrete
    dt 0.1
    n 2 m 1 p 1
    A 1.0 0.1 0.0 1.0
    B 0.0 0.1
    C 1.0 0.0
}

horizon ga_reference_rollout finite 50

ga evolve on ga_reference over ga_reference_rollout -> ref_k1 ref_k2 {
    population 12
    generations 30
    mutation 0.3
}

analyze ga_reference ga report_k1 report_k2 over ga_reference_rollout -> reference_report {
    full
}
```

Complete demos:

```bash
FLOW_HOST=python ./flow run examples/dynamics/ga_control.flow
FLOW_HOST=python ./flow run examples/dynamics/ga_dsys_syntax.flow
```

## WFC coupling

`wfc.flow` provides deterministic tile grids, constraints, propagation, entropy selection, and collapse. `wfc_ga_coupling.flow` couples analysis results and evolved gains into WFC bias/guidance helpers.

```bash
FLOW_HOST=python ./flow run examples/dynamics/ga_wfc_coupled.flow
```

## Validation

Low-level dynamics code should be checked against known matrix results, controllability/rank expectations, spectral radii, Gramian references, rollout trajectories, and deterministic GA seeds. Complete demos are the documentation anchors because they include all storage and import context and are exercised by repository tests.

See also [Dynamics DSL](../language/dynamics-dsl.md), [Evolution and dynamics](../book/13-evolution-and-dynamics.md), and the source under `lib/stdlib/dynamics/`.
