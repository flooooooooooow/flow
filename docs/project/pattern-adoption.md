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
| P0 | Lorenz as `flow` + phase-portrait trail | language + demo ✅ partial | [#165](https://github.com/flooooooooooow/flow/issues/165) |
| P1 | Route linalg examples through `blas.flow` | adoption ✅ | [#168](https://github.com/flooooooooooow/flow/issues/168) |
| P1 | Wire ML demos through Dual / grad codegen | adoption + docs ✅ | [#170](https://github.com/flooooooooooow/flow/issues/170) |
| P1 | Owned `HttpResponse` + JSON decode helpers | API ✅ | [#167](https://github.com/flooooooooooow/flow/issues/167) |
| P2 | Dynamics DSL / LQR beyond n=2 | language + stdlib ✅ partial | [#162](https://github.com/flooooooooooow/flow/issues/162) |
| P2 | Field / `laplacian` PDE surface | language ✅ partial | [#163](https://github.com/flooooooooooow/flow/issues/163) |
| P2 | Dual + Tensor operators + mutable params | language ✅ partial | [#161](https://github.com/flooooooooooow/flow/issues/161) |
| P2 | Closed-loop `plant.step` from `dsys` / `connect` | stdlib + lowering | [#160](https://github.com/flooooooooooow/flow/issues/160) |

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

```flow
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

```flow
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

```flow
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
   (`trail_push_2d`, `trail_index`, `project_axis`); draw loop still in `main`
   until `represent phase_portrait` lowers.

**Exit:** no manual `nxt[]` ODE copy ✅; file ~80 lines (grammar card still open for ≤60).

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

**Follow-on:** LAPACK DARE; `analyze { lqr { … } }` for n>2 in the DSL.

**Exit (stdlib):** Cartpole control has no private mini-ARE. ✅ DSL card open.

---

### 8. Field / `laplacian` PDE

**Shipped MVP:** `lib/stdlib/dynamics/pde.flow` (`laplacian_1d`,
`laplacian_1d_at`, `heat_euler_step_1d`). Tourist
`examples/evolution/heat_diffusion.flow` steps via the helper.

**North-star grammar (follow-on):**
```flow
field T : f64[32] on Line
param alpha : f64 = 0.1

T evolves as alpha * laplacian(T)
boundary T { left = 1.0  right = 0.0 }
```

**Exit (stdlib):** heat demo reads as evolution via laplacian helper, not
nested index soup. ✅ Grammar card remains open.

---

### 9. Dual / Tensor operators + mutable params

**Shipped (Dual ops):** `a * a + 3.0 * x + 1.0` lowers to Dual
overloads (`mul`/`add`/…) in the C generator + typechecker. Demo:
`examples/ml/autodiff/dual_ops.flow`.

**Still open:** mutable struct fields / param-vector updates so `nn.flow`
drops multi-way `param_set` rebuilds; Tensor operators.

```flow
let y: Dual = sin(a * a + b)   # shipped for Dual arithmetic
struct Net { mut w: … }        # follow-on
```

---

### 10. Closed-loop `plant.step`

**Today:** `spring_mass_control.flow` analyzes with `dsys`, then re-hardcodes
A/B Euler in `main`.

**Sketch:**
```flow
flow Plant { … evolves as … }
flow Ctrl { … }
flow Closed {
    plant : Plant
    ctrl  : Ctrl
    connect { plant.y -> ctrl.y;  ctrl.u -> plant.u }
}
# main
let mut s = Closed_new()
Closed_step(&s, dt)
```

Reuse shipped `connect`; add helper that builds a steppable plant from
`represent linear` / analyzed `dsys` so analysis and simulation share one model.

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
