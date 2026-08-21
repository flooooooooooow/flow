# Dynamics Library

API reference for `lib/stdlib/dynamics/` — linear algebra, dynamical-system
types, state-space simulation, Gramians, nonlinear attractors, GA-based gain
search, and Wave Function Collapse coupling.

Design note: the library is allocation-free. Matrices wrap **caller-provided
buffers** (`ptr<f64>` plus dimensions), so every constructor and most analyses
take scratch arrays you declare at the call site. The
[`dsys` surface syntax](../language/dynamics-dsl.md) generates all of this
boilerplate for you; this page documents the functions it expands into.

## Modules

1. [linalg.flow](#linalgflow) — `Matrix` + operations
2. [core.flow](#coreflow) — `DynamicalSystem`, `Horizon`, constructors
3. [state_space.flow](#state_spaceflow) — stepping, rollout, controllability
4. [gramian.flow](#gramianflow) — controllability/observability Gramians
5. [attractor.flow](#attractorflow) — nonlinear fields, RK4, Lyapunov proxy
6. [ga.flow](#gaflow) — genetic gain search
7. [ga_analysis.flow](#ga_analysisflow) — unified GA + control analysis
8. [wfc.flow](#wfcflow) — Wave Function Collapse grids
9. [wfc_ga_coupling.flow](#wfc_ga_couplingflow) — GA-guided WFC evolution

---

## linalg.flow

`import "stdlib/dynamics/linalg.flow"`

Row-major dense matrices over `f64`.

```flow id=matrix
struct Matrix {
    data: ptr<f64>,
    rows: i32,
    cols: i32
}
```

| Function | Signature | Description |
|----------|-----------|-------------|
| `matrix_zeros` | `(data: ptr<f64>, rows: i32, cols: i32) -> Matrix` | Zero-fill buffer, wrap as Matrix |
| `matrix_identity` | `(data: ptr<f64>, n: i32) -> Matrix` | n x n identity |
| `matrix_get` | `(m: Matrix, i: i32, j: i32) -> f64` | Element read |
| `matrix_set` | `(m: Matrix, i: i32, j: i32, val: f64) -> void` | Element write |
| `matrix_copy` | `(src: Matrix, dst: Matrix) -> void` | Copy contents |
| `matrix_add` | `(a: Matrix, b: Matrix, result: Matrix) -> void` | a + b |
| `matrix_sub` | `(a: Matrix, b: Matrix, result: Matrix) -> void` | a - b |
| `matrix_scale` | `(a: Matrix, scalar: f64, result: Matrix) -> void` | scalar * a |
| `matrix_mul` | `(a: Matrix, b: Matrix, result: Matrix) -> void` | Matrix product |
| `matrix_transpose` | `(a: Matrix, result: Matrix) -> void` | a^T |
| `matrix_trace` | `(m: Matrix) -> f64` | Sum of diagonal |
| `matvec` | `(m: Matrix, x: ptr<f64>, y: ptr<f64>) -> void` | y = M x |
| `vec_copy` | `(src: ptr<f64>, dst: ptr<f64>, n: i32) -> void` | Vector copy |
| `vec_scale` | `(x: ptr<f64>, n: i32, s: f64) -> void` | In-place scale |
| `vec_add` | `(a: ptr<f64>, b: ptr<f64>, n: i32, out: ptr<f64>) -> void` | out = a + b |
| `vec_dot` | `(a: ptr<f64>, b: ptr<f64>, n: i32) -> f64` | Dot product |
| `vec_norm` | `(x: ptr<f64>, n: i32) -> f64` | Euclidean norm |

```flow
import "stdlib/dynamics/linalg.flow"

let mut buf: array<f64, 4> = [1.0, 2.0, 3.0, 4.0]
let A: Matrix = Matrix { data: buf, rows: 2, cols: 2 }
let tr: f64 = matrix_trace(A)   # 5.0
```

---

## core.flow

`import "stdlib/dynamics/core.flow"`

Core types for linear time-invariant systems.

```flow uses=matrix
# kind: 0 = discrete x[k+1] = A x + B u,  1 = continuous x' = A x + B u
struct DynamicalSystem {
    n: i32, m: i32, p: i32,   # states, inputs, outputs
    dt: f64,
    kind: i32,
    A: Matrix, B: Matrix, C: Matrix
}

# finite=1 → N-step horizon; finite=0 → infinite horizon (gamma discount)
struct Horizon { finite: i32, steps: i32, gamma: f64 }

# kind: 0 identity, 1 similarity x = T z, 2 modal
struct TransformSpec { kind: i32, T: Matrix, T_inv: Matrix }
```

| Function | Signature | Description |
|----------|-----------|-------------|
| `dsys_discrete` | `(n, m, p: i32, dt: f64, A, B, C: Matrix) -> DynamicalSystem` | Discrete-time system |
| `dsys_continuous` | `(n, m, p: i32, dt: f64, A, B, C: Matrix) -> DynamicalSystem` | Continuous-time system |
| `dsys_euler_discretize` | `(sys: DynamicalSystem, Ad_buf, Bd_buf, id_buf, scaled_buf: ptr<f64>) -> DynamicalSystem` | Euler: `Ad = I + dt*A`, `Bd = dt*B` |
| `horizon_finite` | `(steps: i32) -> Horizon` | N-step horizon |
| `horizon_infinite` | `(gamma: f64) -> Horizon` | Discounted infinite horizon |
| `transform_identity` | `(T_buf: ptr<f64>, n: i32) -> TransformSpec` | Identity transform |
| `transform_similarity` | `(T: Matrix, T_inv: Matrix) -> TransformSpec` | Similarity transform spec |

```flow id=system
import "stdlib/dynamics/core.flow"

let mut a_buf: array<f64, 4> = [1.0, 0.1, 0.0, 1.0]
let mut b_buf: array<f64, 2> = [0.0, 1.0]
let mut c_buf: array<f64, 2> = [1.0, 0.0]

let A: Matrix = Matrix { data: a_buf, rows: 2, cols: 2 }
let B: Matrix = Matrix { data: b_buf, rows: 2, cols: 1 }
let C: Matrix = Matrix { data: c_buf, rows: 1, cols: 2 }
let sys: DynamicalSystem = dsys_discrete(2, 1, 1, 0.1, A, B, C)
let h: Horizon = horizon_finite(50)
```

---

## state_space.flow

`import "stdlib/dynamics/state_space.flow"`

Simulation and structural analysis. Internal scratch arrays cap the state
dimension at 8 and inputs at 4.

| Function | Signature | Description |
|----------|-----------|-------------|
| `state_step` | `(sys: DynamicalSystem, x, u, x_next: ptr<f64>) -> void` | One discrete step `x+ = A x + B u` |
| `state_step_continuous_euler` | `(sys: DynamicalSystem, x, u, x_next: ptr<f64>) -> void` | One Euler step of `x' = A x + B u` |
| `rollout_discrete` | `(sys: DynamicalSystem, x0, u_seq: ptr<f64>, steps: i32, x_out: ptr<f64>) -> void` | Simulate `steps` steps, log states to `x_out` (steps x n) |
| `build_controllability_matrix` | `(sys: DynamicalSystem, ctrl_buf, a_pow_buf, block_buf, next_a_buf: ptr<f64>) -> Matrix` | `[B, AB, …, A^(n-1)B]` |
| `matrix_rank_estimate` | `(m: Matrix, scratch: ptr<f64>) -> i32` | Rank via Gaussian elimination (1e-9 pivot tolerance) |
| `is_controllable` | `(sys: DynamicalSystem, ctrl_buf, a_pow_buf, block_buf, next_a_buf, rank_scratch: ptr<f64>) -> i32` | 1 if `rank(ctrb) >= n` |
| `apply_similarity` | `(sys: DynamicalSystem, spec: TransformSpec, out_a, out_b, work: ptr<f64>) -> DynamicalSystem` | `A' = T^-1 A T`, `B' = T^-1 B` |

```flow uses=system
import "stdlib/dynamics/state_space.flow"

let c1: array<f64, 4> = [0.0, 0.0, 0.0, 0.0]
let c2: array<f64, 4> = [0.0, 0.0, 0.0, 0.0]
let c3: array<f64, 4> = [0.0, 0.0, 0.0, 0.0]
let c4: array<f64, 4> = [0.0, 0.0, 0.0, 0.0]
let c5: array<f64, 4> = [0.0, 0.0, 0.0, 0.0]
let ok: i32 = is_controllable(sys, c1, c2, c3, c4, c5)
```

Full demo: [`examples/dynamics/controllability_demo.flow`](../../examples/dynamics/controllability_demo.flow).

---

## gramian.flow

`import "stdlib/dynamics/gramian.flow"`

Controllability and observability Gramians.
Finite horizon: `Wc(N) = sum A^k B B^T (A^k)^T`. Infinite horizon: iterative
Lyapunov solve `Wc = gamma * A Wc A^T + B B^T` (64 fixed-point iterations).

| Function | Signature | Description |
|----------|-----------|-------------|
| `gramian_finite_horizon` | `(sys: DynamicalSystem, h: Horizon, W_buf, a_pow_buf, block_buf, next_a_buf: ptr<f64>) -> Matrix` | N-step controllability Gramian |
| `gramian_infinite_horizon` | `(sys: DynamicalSystem, h: Horizon, W_buf, bbt_buf, scratch_a, scratch_b: ptr<f64>) -> Matrix` | Discounted Lyapunov Gramian |
| `observability_gramian_finite` | `(sys: DynamicalSystem, h: Horizon, W_buf, a_pow_buf, block_buf, scratch: ptr<f64>) -> Matrix` | N-step observability Gramian |
| `gramian_add_outer` | `(block: Matrix, W: Matrix) -> void` | `W += block * block^T` (helper) |

```flow uses=system
import "stdlib/dynamics/gramian.flow"

# Scratch: the Gramian itself plus three n x n workspaces.
let mut wb: array<f64, 4> = [0.0, 0.0, 0.0, 0.0]
let mut s1: array<f64, 4> = [0.0, 0.0, 0.0, 0.0]
let mut s2: array<f64, 4> = [0.0, 0.0, 0.0, 0.0]
let mut s3: array<f64, 4> = [0.0, 0.0, 0.0, 0.0]

let W: Matrix = gramian_finite_horizon(sys, horizon_finite(50), wb, s1, s2, s3)
let reach_energy: f64 = matrix_trace(W)
```

Full demo: [`examples/dynamics/gramian_demo.flow`](../../examples/dynamics/gramian_demo.flow).

---

## attractor.flow

`import "stdlib/dynamics/attractor.flow"`

Nonlinear flows selected by `sys_id`, integrated with RK4 (state dimension up
to 8):

- `sys_id 0` — damped oscillator `x' = y, y' = -x - 0.5 y`
- `sys_id 1` — Lorenz (sigma=10, rho=28, beta=8/3)
- `sys_id 2` — bistable gradient `x' = x - x^3`

| Function | Signature | Description |
|----------|-----------|-------------|
| `attractor_field` | `(x: ptr<f64>, n: i32, sys_id: i32, out: ptr<f64>) -> void` | Evaluate the vector field at x |
| `rk4_step_n` | `(x: ptr<f64>, n: i32, dt: f64, sys_id: i32, out: ptr<f64>) -> void` | One RK4 step |
| `integrate_attractor` | `(x0: ptr<f64>, n: i32, steps: i32, dt: f64, sys_id: i32, traj: ptr<f64>) -> void` | Integrate, log trajectory (steps x n) |
| `lyapunov_proxy` | `(x0: ptr<f64>, n: i32, steps: i32, dt: f64, sys_id: i32, eps: f64, traj_a, traj_b: ptr<f64>) -> f64` | Finite-time Lyapunov exponent proxy: log separation growth of two nearby trajectories |

```flow
import "stdlib/dynamics/attractor.flow"

let x0: array<f64, 3> = [1.0, 1.0, 1.0]
let ta: array<f64, 300> = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
let tb: array<f64, 300> = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
let lyap: f64 = lyapunov_proxy(x0, 3, 100, 0.01, 1, 1e-6, ta, tb)  # > 0: chaos
```

Full demos: [`examples/dynamics/lorenz_attractor.flow`](../../examples/dynamics/lorenz_attractor.flow),
[`examples/evolution/lorenz_gfx.flow`](../../examples/evolution/lorenz_gfx.flow) (live window).

---

## ga.flow

`import "stdlib/dynamics/ga.flow"`

Elitist genetic algorithm searching state-feedback gains `u = -k1 x1 - k2 x2`
for a 2-state plant.

```flow
struct GAConfig {
    population: i32,
    generations: i32,
    horizon: i32,
    mutation: f64
}
```

| Function | Signature | Description |
|----------|-----------|-------------|
| `ga_rollout_cost` | `(sys: DynamicalSystem, k1: f64, k2: f64, steps: i32) -> f64` | Quadratic cost `sum(x1^2 + x2^2 + 0.1 u^2)` from `x0 = [1, 0]` |
| `ga_evolve_control` | `(sys: DynamicalSystem, steps: i32, cfg: GAConfig, k1_pop, k2_pop, fit_pop, best_k1, best_k2: ptr<f64>) -> f64` | Evolve gains; best written to `best_k1[0]`, `best_k2[0]`; returns best fitness (negated cost) |
| `ga_mutate` | `(val: f64, scale: f64, seed: i32) -> f64` | Deterministic hash-noise mutation |
| `ga_hash` | `(seed: i32) -> f64` | LCG-style hash in [0, 1) |

```flow uses=system
import "stdlib/dynamics/ga.flow"

let cfg: GAConfig = GAConfig { population: 12, generations: 30, horizon: 50, mutation: 0.3 }
# Scratch: one slot per individual for each gain and its fitness, plus the
# two best-so-far gains.
let mut k1p: array<f64, 12> = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
let mut k2p: array<f64, 12> = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
let mut fp: array<f64, 12> = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
let mut bk1: array<f64, 1> = [0.0]
let mut bk2: array<f64, 1> = [0.0]

let fit: f64 = ga_evolve_control(sys, 50, cfg, k1p, k2p, fp, bk1, bk2)
```

Full demo: [`examples/dynamics/ga_control.flow`](../../examples/dynamics/ga_control.flow).

---

## ga_analysis.flow

`import "stdlib/dynamics/ga_analysis.flow"`

Unified analysis treating plant, GA-closed loop, and the GA fitness trajectory
as coupled dynamical systems. This is what `analyze … -> report` in the
[dsys DSL](../language/dynamics-dsl.md) expands to.

```flow
struct GAAnalysisReport {
    plant_controllable: i32,
    plant_spectral_radius: f64,
    closed_spectral_radius: f64,
    gramian_open_finite: f64,
    gramian_open_infinite: f64,
    closed_loop_energy: f64,
    baseline_cost: f64,
    evolved_cost: f64,
    fitness_drop: f64,
    convergence_gen: i32,
    stable_closed_loop: i32
}
```

| Function | Signature | Description |
|----------|-----------|-------------|
| `ga_closed_loop_matrix` | `(sys: DynamicalSystem, k1: f64, k2: f64, acl_buf, bk_buf: ptr<f64>) -> DynamicalSystem` | Closed loop `x+ = (A - B K) x` for `K = [k1, k2]` |
| `matrix_spectral_radius_2x2` | `(m: Matrix) -> f64` | Exact spectral radius of a 2x2 (handles complex pairs) |
| `ga_evolve_traced` | `(sys, steps, cfg, k1_pop, k2_pop, fit_pop, best_k1, best_k2, cost_history) -> f64` | `ga_evolve_control` + per-generation best-cost history |
| `ga_closed_loop_energy` | `(closed: DynamicalSystem, steps: i32) -> f64` | `sum(x'x)` from `x0 = [1, 0]` under zero input |
| `ga_fitness_convergence_gen` | `(cost_history: ptr<f64>, generations: i32, tol: f64) -> i32` | Generations-from-end where cost settled within tol |
| `ga_analyze_control_search` | `(plant, steps, cfg, …12 scratch buffers) -> GAAnalysisReport` | Full pipeline: baseline, GA, controllability, spectra, Gramians, energy, convergence |

```flow uses=system
import "stdlib/dynamics/ga_analysis.flow"

# Scratch: the closed-loop A, and B times the gain row.
let mut acl: array<f64, 4> = [0.0, 0.0, 0.0, 0.0]
let mut bk: array<f64, 4> = [0.0, 0.0, 0.0, 0.0]

let closed: DynamicalSystem = ga_closed_loop_matrix(sys, 2.5, 3.5, acl, bk)
let rho: f64 = matrix_spectral_radius_2x2(closed.A)   # < 1.0 → stable
```

Full demo: [`examples/dynamics/ga_full_analysis.flow`](../../examples/dynamics/ga_full_analysis.flow).

---

## wfc.flow

`import "stdlib/dynamics/wfc.flow"`

Wave Function Collapse: constraint propagation on tile grids. Tiles 0-3
(empty/wall/floor/door) with N/E/S/W socket compatibility.

```flow
struct WFCTile { id: i32, north: i32, east: i32, south: i32, west: i32 }
struct WFCGrid { width: i32, height: i32, cells: ptr<i32>, options: ptr<i32> }
```

`cells[i] = -1` means uncollapsed; `options` is a `cells x tiles` 0/1 mask.

| Function | Signature | Description |
|----------|-----------|-------------|
| `wfc_tile_table` | `(tid: i32) -> WFCTile` | Socket table for tile id |
| `wfc_compatible` | `(a: WFCTile, b: WFCTile, dir: i32) -> i32` | Socket match in direction (0=N 1=E 2=S 3=W) |
| `wfc_propagate` | `(grid: WFCGrid, tile_count: i32) -> i32` | Constraint propagation to fixpoint (guard 64 sweeps) |
| `wfc_step` | `(grid: WFCGrid, tile_count: i32, seed: i32) -> i32` | Collapse the lowest-entropy cell; 0 when none left |
| `wfc_run_collapse` | `(grid: WFCGrid, tile_count: i32, seed: i32, max_steps: i32) -> i32` | Propagate + step until done or budget |
| `wfc_count_collapsed` | `(grid: WFCGrid) -> i32` | Number of decided cells |
| `wfc_wall_fraction` | `(grid: WFCGrid) -> f64` | Fraction of cells that are walls |
| `wfc_mean_entropy` | `(grid: WFCGrid, tile_count: i32) -> f64` | Mean option count of undecided cells |

Full demo: [`examples/dynamics/wfc_demo.flow`](../../examples/dynamics/wfc_demo.flow).

---

## wfc_ga_coupling.flow

`import "stdlib/dynamics/wfc_ga_coupling.flow"`

Couples the three layers: GA analysis biases WFC collapse, and the collapsed
layout's statistics scale the plant's input and initial state.

```flow
struct CoupledGuidance { seed: i32, max_steps: i32, b_scale: f64, layout_bias: f64 }
struct WFCRunReport { collapsed: i32, steps_taken: i32, wall_fraction: f64, mean_entropy: f64 }
struct GuidedEvolutionReport {
    input_scale: f64, layout_energy: f64,
    guided_spectral_radius: f64, collapsed_cells: i32, stable_guided: i32
}
```

| Function | Signature | Description |
|----------|-----------|-------------|
| `couple_ga_wfc_guidance` | `(report: GAAnalysisReport, k1: f64, k2: f64, base_seed: i32, base_steps: i32) -> CoupledGuidance` | Derive WFC seed/budget and input scaling from GA results |
| `wfc_run_guided` | `(grid: WFCGrid, tile_count: i32, guide: CoupledGuidance) -> WFCRunReport` | Run collapse under guidance, report statistics |
| `dsys_scale_input` | `(sys: DynamicalSystem, scale: f64, b_buf: ptr<f64>) -> DynamicalSystem` | Scale the B matrix |
| `layout_state_bias` | `(wfc: WFCRunReport, guide: CoupledGuidance) -> f64` | Initial-state bias from layout openness |
| `guided_layout_rollout_energy` | `(closed: DynamicalSystem, state_bias: f64, steps: i32) -> f64` | Rollout energy from the biased initial state |
| `guide_state_evolution` | `(plant, k1, k2, guide, wfc, steps, b_buf, acl_buf, bk_buf) -> GuidedEvolutionReport` | Full guided-evolution pipeline |

Full demo: [`examples/dynamics/ga_wfc_coupled.flow`](../../examples/dynamics/ga_wfc_coupled.flow).

---

## See also

- [Dynamics DSL reference](../language/dynamics-dsl.md) — the `dsys` surface syntax that generates calls into this library
- [Dynamics tutorial](../tutorials/dynamics.md) — modeling systems that evolve through time
- [`examples/evolution/`](../../examples/evolution/README.md) — the flagship vision suite built on this library
