# Pattern Adoption — Less Code, Cooler Surfaces

> Companion to [ROADMAP.md](../../ROADMAP.md) (repo root) and the GitHub `[roadmap]` / `[patterns *]` issues.
> Goal: where Flow already has (or almost has) a distinctive pattern, **use it** in
> canonical examples; where ceremony is still C-shaped, **sketch a readable surface**
> and implement it.

Last updated: 2026-08-05.

---

## Thesis

Flow’s differentiator is **evolution + analysis as syntax**. Hand-rolled RK4,
`mat_get`/`mat_set` nests, and `dense_backward` in showcase programs undermine that
story. Adoption first; new sugar second.

| Priority | Item | Kind | Issue |
|----------|------|------|-------|
| P0 | Canonicalize evolution demos onto `flow` / `evolves` / `when` | adoption ✅ | [#159](https://github.com/flooooooooooow/flow/issues/159) |
| P0 | `gfx_run` frame helper | stdlib ✅ | [#164](https://github.com/flooooooooooow/flow/issues/164) |
| P0 | Lorenz as `flow` + phase-portrait trail | language + demo ✅ | [#165](https://github.com/flooooooooooow/flow/issues/165) |
| P1 | Route linalg examples through `blas.flow` | adoption ✅ | [#168](https://github.com/flooooooooooow/flow/issues/168) |
| P1 | Wire ML demos through Dual / grad codegen | adoption + docs ✅ | [#170](https://github.com/flooooooooooow/flow/issues/170) |
| P1 | Owned `HttpResponse` + JSON decode helpers | API ✅ | [#167](https://github.com/flooooooooooow/flow/issues/167) |
| P2 | Dynamics DSL / LQR beyond n=2 | language + stdlib ✅ | [#162](https://github.com/flooooooooooow/flow/issues/162) |
| P2 | Field / `laplacian` PDE surface | language ✅ | [#163](https://github.com/flooooooooooow/flow/issues/163) |
| P2 | Dual + Tensor operators + mutable params | language ✅ | [#161](https://github.com/flooooooooooow/flow/issues/161) |
| P2 | Closed-loop `plant.step` from `dsys` / `connect` | stdlib + lowering ✅ | [#160](https://github.com/flooooooooooow/flow/issues/160) |

---

## P0 — Adoption & small stdlib

### 1. Canonicalize evolution demos

**Today:** `pendulum.flow`, `bouncing_ball.flow` hand-integrate; `*_evolves.flow`
siblings already show the shipped pattern.

**Target:**
- README / `examples/README.md` / `examples/STATUS.md` point at `*_evolves` /
  `*_rk4` / `*_always` as the teaching path.
- Hand ODE files become “how it lowers” (comment banner + link), not the first hit.
- No new syntax required.

**Exit:** Tourist path (`examples/evolution/`) leads with declarative files; hand
RK4 is clearly marked pedagogical.

---

### 2. `gfx_run` frame helper

**Today** (every gfx demo):

```flow-pseudocode
while frame < MAX {
    if gfx_should_close(g) { break }
    gfx_poll(g)
    if gfx_key_down(g, KEY_ESC) { break }
    gfx_clear(g, ...)
    # draw…
    gfx_present(g)
    frame = frame + 1
}
```

**Sketch A — callback (no new syntax):**

```text
# lib/stdlib/gfx.flow
export function gfx_run(g: Gfx, max_frames: i32, frame_fn: /* FrameFn */) -> i32
# FrameFn(g, frame) -> bool   # return false to quit
```

Until first-class fn pointers are comfortable everywhere, ship a **macro-ish
convention** via generated trampoline *or* a thin C helper:

```c
// runtime: poll / esc / close; call user `flow_gfx_frame(Gfx*, int frame) -> int`
int flow_gfx_run(void *ctx, int max_frames);
```

with Flow demos implementing `function flow_gfx_frame(g: Gfx, frame: i32) -> i32`.

**Sketch B — block sugar (later card):**

```text
gfx_run(g, max_frames: 2000) {
    # body is the frame; `break` / return false ends
    gfx_clear(g, 8, 8, 16)
    # …
}
```

**Recommendation:** Sketch A first (stdlib + runtime), Sketch B only if A proves
awkward. See Questions.md.

**Exit:** Lorenz, Tetris, 2048, cartpole gfx use `gfx_run` (or `flow_gfx_run`).

---

### 3. Lorenz as `flow` + phase portrait

**North-star (already commented in `lorenz_gfx.flow`):**

```flow
flow Lorenz {
    state x : f64 = 1.0
    state y : f64 = 1.0
    state z : f64 = 1.0
    param sigma : f64 = 10.0
    param rho   : f64 = 28.0
    param beta  : f64 = 8.0 / 3.0

    solver { dt 5 ms  method rk4 }

    x evolves as sigma * (y - x)
    y evolves as x * (rho - z) - y
    z evolves as x * y - beta * z

    represent phase_portrait(x, z) {
        trail 320
        window 900, 700
        map x in [-25, 25] -> col
        map z in [0, 55]   -> row
    }
}
```

**MVP split:**
1. Port dynamics to `flow Lorenz` + `solver { method rk4 }` ✅
2. Trail/project helpers in `stdlib/dynamics/portrait.flow` ✅
3. `represent phase_portrait(x, z) { trail…; window…; map… }` lowers to
   `{Name}_portrait_frame` + win/trail consts ✅ (`lorenz_gfx.flow` ~70 lines)

**Exit:** no manual `nxt[]` ODE copy ✅; portrait draw is generated from
`represent` ✅. Window open / `gfx_present` / trail buffers remain in `main`.

---

## P1 — Honesty & API polish

### 4. Linalg → `blas.flow`

**Shipped:** Tourist `lu_decomposition.flow` calls `solve` / `lu_factor`
(`getrf` wrapper). Hand Doolittle → `lu_decomposition_pedagogical.flow`.
`blas_demo.flow` already exercises gemm/solve.

**Exit:** Primary linalg tourist examples call BLAS; index loops only in
“from scratch” files. ✅ (`lu_decomposition.flow` → `solve`/`lu_factor`;
hand Doolittle → `lu_decomposition_pedagogical.flow`)

---

### 5. ML demos → Dual / grad codegen

**Shipped:** Tourist `examples/ml/models/mlp_xor.flow` trains via
`net2x2x1_grads_xor_autogen` (`nn_autogen.flow` + checked-in
`flow_grad_flow.py` output). Hand `dense_backward` lives in
`mlp_xor_from_scratch.flow`. Docs: AD is **stdlib + codegen today**;
compiler `loss.grad` remains a later card (#161).

**Exit:** XOR demo trains without a hand `dense_backward`; overview/README
wording matches reality. ✅

---

### 6. Owned HTTP + JSON helpers

**Shipped:** `registry/packages/http` exports `HttpBody`, `http_get` /
`http_get_cap`, `http_body_free`. `apps/http_json_cache/src/live_http.flow`
uses owned get (no caller `http_alloc` ceremony). JSON helpers already
ship `json_validate` / `json_get_i32`; typed `Result_*` decode is follow-on.

**Exit:** Live HTTP path uses owned body; docs show ≤10-line GET+JSON example. ✅

---

## P2 — New language / analysis surfaces

### 7. Dynamics DSL / LQR beyond n=2

**Shipped MVP:** `lib/stdlib/dynamics/lqr.flow` —
`dlqr_diag_q_scalar_u` / `lqr_diag_q` for n≤8, scalar input. Cartpole
`cartpole_lqr_gains` is a thin wrapper (no private Riccati loop).

**Also shipped:** vision-form DSL
```text
analyze plant {
    lqr {
        Q 1.0 1.0 1.0 1.0
        R 1.0
        -> k0 k1 k2 k3
    }
}
```
→ `dlqr_diag_q_scalar_u` on the (discretized) plant. Demos:
`spring_mass_lqr.flow` (n=2 continuous), `chain4_lqr.flow` (n=4).

**Follow-on:** LAPACK DARE; poles/controllability items in the same
`analyze Name { … }` block.

**Exit (stdlib + DSL lqr):** Cartpole has no private mini-ARE ✅; DSL
`analyze { lqr }` works for n≤8 ✅.

---

### 8. Field / `laplacian` PDE

**Shipped MVP:** `lib/stdlib/dynamics/pde.flow` (`laplacian_1d`,
`laplacian_1d_at`, `heat_euler_step_1d`). Tourist
`examples/evolution/heat_diffusion.flow` steps via the helper.

**Also shipped:** Stage-1 grammar expander (`field_dsl.py`):
```text
field T : f64[32] on Line
T evolves as laplacian(T)
boundary T { left = AMBIENT  right = AMBIENT }
```
→ `T_field_step(u, next, r)`. Heat demo uses this surface.

**Exit:** heat demo reads as field evolution ✅. 2D / `on Plane` follow-on.

---

### 9. Dual / Tensor operators + mutable params

**Shipped (Dual ops):** `a * a + 3.0 * x + 1.0` lowers to Dual
overloads (`mul`/`add`/…) in the C generator + typechecker. Demo:
`examples/ml/autodiff/dual_ops.flow`.

**Also shipped:** `nn.flow` `param_set` / `_step` use mut field assignment
instead of full-struct rebuilds.

**Shipped (Tensor ops):** element-wise `+ - * /` and `t * s` / `t + s`
lower to `tensor_*` helpers. Demo: `examples/ml/autodiff/tensor_ops.flow`.
Matmul stays `tensor_matmul`.

**Still open:** compiler `loss.grad` (optional follow-on).

```text
let y: Dual = sin(a * a + b)   # shipped
let mut n: Net2x2x1 = net
n.w00 = n.w00 - lr * g.dw00    # shipped
let z: Tensor = a * b + 1.0    # shipped (element-wise / add_scalar)
```

**Exit:** AD / NN / Tensor call sites look like math ✅. `loss.grad` card open.

### 10. Closed-loop `plant.step`

**Shipped:** DSL expansion aliases `let plant: DynamicalSystem = __dsys_plant`.
`spring_mass_control.flow` steps with `plant_step(plant, …)`. `plant_step` is
an alias of `state_step`.

**Follow-on:** nonlinear `connect` Closed_step sharing analysis plant
(`robot_connect` already shows composition shape).

---

## Non-goals (this wave)

- Full compiler reverse-mode tape AD
- Resumable effect TCP replacing registry HTTP
- Verify tactics / Nat corpus collapse (separate epistemology track)
- Exact event-time refinement inside RK4 (hybrid card follow-on)

---

## References

- [VISION.md](../../VISION.md) — evolution thesis
- [north-star.md](../vision/north-star.md) — shipped `flow` / `evolves` / `when` / `connect` cards
- [dynamics-dsl.md](../language/dynamics-dsl.md) — `dsys` / `analyze`
- Examples: `examples/evolution/pendulum_evolves.flow`, `lorenz_gfx.flow`,
  `spring_mass_control.flow`, `apps/cartpole/`
