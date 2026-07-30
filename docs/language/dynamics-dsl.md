# Dynamics DSL (`dsys`)

Flow ships a declarative surface syntax for linear dynamical systems: declare a
plant, analyze it (controllability, spectral radius, Gramians), evolve feedback
gains with a genetic algorithm, and certify the closed loop — all as top-level
blocks, with zero matrix boilerplate.

**How it works (honestly):** the `dsys` vocabulary is not part of the core
grammar. It is a **pre-parse expander** (`src/flow/dynamics_dsl.py`, hooked
into `src/flow/module_resolver.py`) that runs before the real parser sees your
source. The blocks below are stripped from the file, compiled into ordinary
calls to the [`stdlib/dynamics` library](../library/dynamics.md), and the
generated setup code is injected at the top of `main()`'s body (importing
`stdlib/dynamics/ga_analysis.flow` — or `wfc_ga_coupling.flow` when WFC blocks
are present — automatically). The bound names (`plant_ok`, `k1`, …) become
ordinary local variables of `main`.

Working examples:

- [`examples/dynamics/ga_dsys_syntax.flow`](../../examples/dynamics/ga_dsys_syntax.flow) — every analysis block in one file
- [`examples/evolution/spring_mass_control.flow`](../../examples/evolution/spring_mass_control.flow) — continuous plant, model → analyze → control → certify

## Current envelope

The shipped machinery targets **2-state, single-input, single-output discrete
LTI systems** (`n 2 m 1 p 1`). Spectral-radius bindings use a closed-form 2x2
eigenvalue solve, and the internal scratch buffers the expander emits are sized
for n = 2. Continuous declarations are supported and are Euler-discretized
(`Ad = I + dt*A`, `Bd = dt*B`) before analysis. Keep `generations` at 32 or
below — the GA convergence history buffer holds 32 entries.

---

## `dsys` — declare a system

```flow
dsys plant {
    discrete            # or: continuous (Euler-discretized at dt)
    dt 0.1              # sample period / integration step
    n 2 m 1 p 1         # states, inputs, outputs
    A 1.0 0.1 0.0 1.0   # row-major, n*n entries
    B 0.0 0.1           # n*m entries
    C 1.0 0.0           # p*n entries
}
```

Defaults if a line is omitted: `discrete`, `dt 0.1`, `n 2 m 1 p 1`.
`discrete` means `x[k+1] = A x[k] + B u[k]`; `continuous` means
`x' = A x + B u`, discretized by the compiler before any analysis runs.

## `horizon` — name an analysis horizon

```flow
horizon rollout finite 50              # 50 steps
horizon asymptotic infinite gamma 0.99 # discounted infinite horizon
```

Horizons are referenced by name from `sense`, `ga evolve`, `closed`, and
`analyze` blocks.

## `sense` — analyze the open loop

```flow
sense on plant {
    controllable -> plant_ok                    # i32: 1 if rank(ctrb) == n
    spectral -> rho_open                        # f64: spectral radius of A (2x2)
    gramian finite rollout trace -> wc_fin      # f64: trace of Wc over the horizon
    gramian infinite asymptotic trace -> wc_inf # f64: trace of the Lyapunov Wc
}
```

Each line binds one measurement to a fresh variable, visible in `main()`.
`gramian finite`/`gramian infinite` name a horizon declared earlier; only the
trace of the controllability Gramian is bound.

## `ga evolve` — search feedback gains

```flow
ga evolve on plant over rollout -> k1 k2 {
    population 12    # default 8
    generations 30   # default 20 (max 32)
    mutation 0.3     # default 0.3
}
```

Runs an elitist genetic algorithm over state-feedback gains
`u = -k1*x1 - k2*x2`, minimizing the quadratic rollout cost
`sum(x1^2 + x2^2 + 0.1 u^2)` from `x0 = [1, 0]` over the named horizon. The
best gains are bound to the two variables after the `->`.

## `closed` — certify the closed loop

```flow
closed plant with k1 k2 {
    spectral -> rho_cl          # f64: spectral radius of A - B*K
    energy over rollout -> E_cl # f64: sum of x'x over the horizon
    stable -> stable_cl         # i32: 1 if rho(A - B*K) < 1
}
```

Forms the closed-loop matrix `A - B*K` from the evolved (or hand-written)
gains and re-analyzes it.

## `analyze` — one-shot unified report

```flow
analyze plant ga k1 k2 over rollout -> report {
    full
}
```

Runs the whole pipeline — baseline cost, GA search, controllability, open- and
closed-loop spectral radii, finite/infinite Gramian traces, closed-loop
energy, convergence generation — and binds a `GAAnalysisReport` struct (fields
like `report.fitness_drop`, `report.closed_spectral_radius`,
`report.stable_closed_loop`; see
[the library reference](../library/dynamics.md#ga_analysisflow)). It also
assigns `k1`/`k2` from its own GA run. If a `ga evolve` block exists for the
same system and horizon, its population/generations/mutation settings are
reused; otherwise defaults are 12/30/0.3.

## WFC coupling blocks (experimental)

The same expander also understands `wfc field NAME { size … tiles … seed …
pin … collapse … }`, `couple SYS field NAME using report k1 k2 { … }`, and
`guide SYS with k1 k2 through NAME using guide over HZ { … }`, which couple GA
analysis to a Wave Function Collapse constraint field
(`stdlib/dynamics/wfc_ga_coupling.flow`). See
[`examples/dynamics/ga_wfc_coupled.flow`](../../examples/dynamics/ga_wfc_coupled.flow).

---

## Complete minimal example

This program compiles and runs today (`./flow run`):

```flow
extern {
    function printf(fmt: string, val: f64) -> i32
}

dsys plant {
    discrete
    dt 0.1
    n 2 m 1 p 1
    A 1.0 0.1 0.0 1.0
    B 0.0 0.1
    C 1.0 0.0
}

horizon rollout finite 50

sense on plant {
    controllable -> plant_ok
    spectral -> rho_open
}

ga evolve on plant over rollout -> k1 k2 {
    population 12
    generations 30
    mutation 0.3
}

closed plant with k1 k2 {
    spectral -> rho_cl
    stable -> stable_cl
}

function main() -> i32 {
    if plant_ok == 1 { println("controllable: yes") }
    print("open-loop  spectral radius: ")
    printf("%.4f", rho_open)
    println("")
    print("evolved gains: k1 = ")
    printf("%.4f", k1)
    print(", k2 = ")
    printf("%.4f", k2)
    println("")
    print("closed-loop spectral radius: ")
    printf("%.4f", rho_cl)
    println("")
    if stable_cl == 1 { println("closed loop stable: yes") }
    return 0
}
```

Output:

```
controllable: yes
open-loop  spectral radius: 1.0000
evolved gains: k1 = 2.5494, k2 = 3.5328
closed-loop spectral radius: 0.8989
closed loop stable: yes
```

The double integrator is marginally stable open loop (rho = 1); the evolved
feedback pulls the spectral radius inside the unit circle.

---

## Today vs north-star

The `dsys` vocabulary is the shipped seed of Flow's founding vision
([`VISION.md`](../../VISION.md)): a language whose primary abstraction is the
**evolution of systems through time**. The mapping:

| Today (shipped) | North-star (aspirational) |
|---|---|
| `dsys plant { A … B … C … }` | `flow Plant { position : Meter; … }` with typed, unit-checked state |
| matrices as flat numbers | `position evolves as velocity` — dynamics as equations, any nonlinearity |
| `when height reaches 0.0 { velocity becomes -0.8 * velocity }` | event location by root-finding inside the step; boolean edge guards |
| `continuous` + Euler discretization | solver selection in a `deploy { solver RK4 }` block |
| `every 100 ms { heater becomes … }` + `solver { dt 1 ms }` | multi-rate composition via `connect`; `after … within 200 ms` temporal guarantees |
| `sense on plant { controllable … }` | `analyze Plant { poles, stability, controllability, observability }` |
| `ga evolve on … { … }` | `control Plant { objective { minimize error } }` — PID/LQR/MPC synthesis |
| `closed … { stable -> s }` + runtime check | `guarantee { stable }` — compilation fails if unprovable |
| pre-parse text expansion | first-class grammar, type-checked `flow` declarations |

The first north-star card has shipped: `evolves as` now compiles. A
`flow Name { ... }` block with `state`, `param`, `input`, and `output`
members and `x evolves as expr` dynamics parses as real AST, passes the
strict type checker, and lowers to C as a struct plus
`Name_step(Name* self, double dt)` with explicit Euler and a separate
`Name_derivs` function, so a later card can swap in RK4 without changing
the surface syntax. All derivatives are evaluated from the pre-step state.
See `examples/evolution/pendulum_evolves.flow` for the pendulum written
this way.

Hybrid events have shipped in their zero-crossing form:
`when x reaches L { x becomes expr }` inside a flow block fires when the
sign of `x - L` changes between the end of one step and the next, then
applies its `becomes` resets synchronously, all right-hand sides read
from the same pre-reset state. Detection is at step granularity; locating
the crossing inside the step is a later refinement. See
`examples/evolution/bouncing_ball_evolves.flow` for the bouncing ball
written this way.

Time blocks have shipped. Duration literals (`10 ms`, `500 us`, suffixes
`ns`/`us`/`ms`/`s`/`min`) canonicalize to i64 nanoseconds at parse time.
An `every <duration> { x becomes expr }` block inside a flow fires once
per elapsed period of integrated time, with a catch-up loop when one step
covers several periods, lowered to a hidden nanosecond accumulator in the
struct. A `solver { dt 1 ms  method euler }` block pins the default fixed
step, generated as `Name_default_dt()`; `Name_step` keeps caller-supplied
dt. See `examples/evolution/thermostat_evolves.flow` for a sampled
bang-bang controller written this way. Invariants and `connect` remain
aspirational.

The strategy is to grow this seed rather than build a second language beside
the current one. The concrete grammar-level plan for each north-star construct
— what `evolves as` desugars to, how time blocks and hybrid events land — is
specified in [docs/vision/north-star.md](../vision/north-star.md), with
aspirational example programs in
[docs/vision/examples/](../vision/examples/). For the vision itself, read
[`VISION.md`](../../VISION.md) (distilled on the [Vision page](../vision.md));
for what the gap looks like in practice, every file in
[`examples/evolution/`](../../examples/evolution/README.md) opens with a
North-star comment showing how the same system will read one day.

## MLIR backend status

Programs that use structs, including every `flow` block, now execute through
the MLIR pipeline (`./flow jit` and `./flow mlir-run`) with the same results
as the C backend. Struct literals, field reads, field stores, address-of, and
pointer-to-struct parameters all lower to LLVM-dialect ops (insertvalue,
extractvalue, getelementptr, load, store).
`examples/evolution/pendulum_evolves.flow` and
`tests/core/test_evolves_pendulum.flow` both pass under the JIT.
Effect handlers and their vtables do not lower through MLIR yet; programs
that use effects still need the C backend.
