# examples/dynamics — dynamical systems, analysis, and control

Examples for the [`stdlib/dynamics` library](../../docs/library/dynamics.md)
and the declarative [`dsys` surface syntax](../../docs/language/dynamics-dsl.md)
(a pre-parse expander, `src/flow/dynamics_dsl.py`). Run any of them with
`./flow run examples/dynamics/<file>`.

| File | What it shows |
|---|---|
| [`controllability_demo.flow`](controllability_demo.flow) | Continuous mass-spring-damper, Euler discretization, controllability rank test, similarity transform (`A' = T^-1 A T`) |
| [`gramian_demo.flow`](gramian_demo.flow) | Finite vs infinite (discounted Lyapunov) horizon controllability Gramians on a double integrator |
| [`lorenz_attractor.flow`](lorenz_attractor.flow) | RK4 integration of the Lorenz system + finite-time Lyapunov separation proxy (chaos detection) |
| [`ga_control.flow`](ga_control.flow) | GA search for stabilizing feedback gains on a discrete double integrator, via direct `stdlib/dynamics/ga.flow` calls |
| [`ga_full_analysis.flow`](ga_full_analysis.flow) | GA search + unified analysis: controllability, Gramians, closed-loop spectral radius, and GA convergence in one `GAAnalysisReport` |
| [`ga_dsys_syntax.flow`](ga_dsys_syntax.flow) | The same analysis as `ga_full_analysis.flow` written in the `dsys` surface syntax — `dsys`, `horizon`, `sense`, `ga evolve`, `closed`, `analyze` blocks, zero matrix boilerplate |
| [`wfc_demo.flow`](wfc_demo.flow) | Wave Function Collapse constraint propagation on a small tile grid |
| [`ga_wfc_coupled.flow`](ga_wfc_coupled.flow) | GA analysis biasing WFC collapse, whose layout statistics then guide scaled state-space evolution (`couple`/`guide` blocks) |

The flagship, self-checking vision examples built on this machinery live in
[`examples/evolution/`](../evolution/README.md).
