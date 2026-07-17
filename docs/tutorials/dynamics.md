# FLOW Tutorial: Dynamics

Modeling systems that evolve through time — from a hand-written integrator to
Flow's declarative `dsys` syntax, analysis, and evolved control. This is the
tutorial for Flow's founding thesis ([VISION.md](../../VISION.md)): programs as
descriptions of **evolution**, not instruction sequences.

Prerequisites: [intermediate.md](intermediate.md) (structs, arrays, `ptr<f64>`).

## Part 1: An ODE Integrator by Hand

Every dynamical program starts from the same loop: state, a derivative, a time
step. Here is explicit Euler for `dy/dt = f(t, y)`:

```flow
function euler_step(t: f64, y: f64, dt: f64, f_idx: i32) -> f64 {
    let dy: f64 = eval_derivative(t, y, f_idx)
    return y + dt * dy
}
```

Euler drifts; the classic fix is Runge-Kutta 4, which samples the derivative
four times per step. Both, plus a midpoint method and accuracy comparisons
against closed-form solutions, live in
[`examples/numerical/ode_solver.flow`](../../examples/numerical/ode_solver.flow):

```bash
./flow run examples/numerical/ode_solver.flow
```

### 1.1 State + events = hybrid systems

A bouncing ball is continuous flight punctuated by discrete impacts. The
event (height reaches zero) is solved *inside* the step, then the reset
`velocity becomes -e * velocity` is applied:

```flow
if h_next <= 0.0 and v < 0.0 {
    # event: exact impact instant within this step
    let tau: f64 = (v + sqrt(v * v + 2.0 * GRAVITY * h)) / GRAVITY
    v = 0.0 - RESTITUTION * (v - GRAVITY * tau)
    h = 0.0
}
```

See [`examples/evolution/bouncing_ball.flow`](../../examples/evolution/bouncing_ball.flow) —
its measured impact times match the closed-form bounce schedule to ~1e-13 s.

---

## Part 2: State-Space Systems with `stdlib/dynamics`

Hand loops don't compose. The dynamics library gives you a first-class system
type — matrices over caller-provided buffers, no allocation:

```flow
import "stdlib/dynamics/state_space.flow"

# mass-spring-damper: x1' = x2, x2' = -x1 - 0.3 x2 + u
let Ac: array<f64, 4> = [0.0, 1.0, -1.0, -0.3]
let Bc: array<f64, 2> = [0.0, 1.0]
let Cc: array<f64, 2> = [1.0, 0.0]
let cont: DynamicalSystem = dsys_continuous(2, 1, 1, 0.05,
    Matrix { data: Ac, rows: 2, cols: 2 },
    Matrix { data: Bc, rows: 2, cols: 1 },
    Matrix { data: Cc, rows: 1, cols: 2 })
```

Discretize it and ask a structural question — *can inputs steer every state?*

```flow
let sys: DynamicalSystem = dsys_euler_discretize(cont, Ad, Bd, Id, sc)

let ok: i32 = is_controllable(sys, c1, c2, c3, c4, c5)   # rank of [B, AB]
```

(The extra arguments are scratch buffers — `array<f64, 4>` each. See the
[library reference](../library/dynamics.md#state_spaceflow) for every
signature.) Run the full version:

```bash
./flow run examples/dynamics/controllability_demo.flow
```

`state_step` advances one step, `rollout_discrete` simulates a whole
trajectory, and [`gramian.flow`](../library/dynamics.md#gramianflow) measures
*how much* input energy it takes to reach states, not just whether you can.

---

## Part 3: The `dsys` Surface Syntax

All that buffer plumbing disappears with the declarative
[dynamics DSL](../language/dynamics-dsl.md) — a pre-parse expander that turns
top-level blocks into the same library calls:

```flow
dsys plant {
    continuous
    dt 0.1
    n 2 m 1 p 1
    A 0.0 1.0 -1.0 -0.2   # mass-spring-damper
    B 0.0 1.0
    C 1.0 0.0
}

horizon rollout finite 60
```

The compiler Euler-discretizes the continuous plant and makes it available to
every analysis block below. No matrices, no scratch arrays.

---

## Part 4: Analysis with `sense`

Ask the plant questions; each answer lands in a fresh variable in `main()`:

```flow
sense on plant {
    controllable -> plant_ok               # 1 if rank(ctrb) == n
    spectral -> rho_open                   # spectral radius of A
    gramian finite rollout trace -> reach  # reachability energy
}
```

`rho_open >= 1` means the discrete plant does not decay on its own — the
mass-spring-damper rings at rho ≈ 0.995, so it barely does.

---

## Part 5: Evolved Control with `ga evolve`

Now close the loop. A genetic algorithm searches feedback gains
`u = -k1 x1 - k2 x2` minimizing a quadratic rollout cost, and a `closed` block
re-certifies the result:

```flow
ga evolve on plant over rollout -> k1 k2 {
    population 16
    generations 40
    mutation 0.3
}

closed plant with k1 k2 {
    spectral -> rho_cl        # spectral radius of A - B*K
    energy over rollout -> E  # closed-loop state energy
    stable -> stable_cl       # 1 if rho < 1
}
```

The whole model → analyze → control → certify pipeline, in one file, is
[`examples/evolution/spring_mass_control.flow`](../../examples/evolution/spring_mass_control.flow):

```bash
./flow run examples/evolution/spring_mass_control.flow
```

```
    controllable          : yes
    open-loop  rho(A)     : 0.9950   (lightly damped ringing)
    evolved gains         : k1 = 2.0310,  k2 = 3.0894
    closed-loop rho(A-BK) : 0.8375
    OK: controllable plant, stable evolved loop, faster settling
```

For everything at once — including a `GAAnalysisReport` struct with baseline
vs evolved cost and convergence generation — use the one-shot form:

```flow
analyze plant ga k1 k2 over rollout -> report { full }
```

---

## Part 6: Where to Go Next

Watch a chaotic system evolve live: the Lorenz attractor stepped by the
stdlib RK4 integrator, drawn into a real window as a fading comet trail:

```bash
./flow gfx examples/evolution/lorenz_gfx.flow
```

Then tour the flagship vision suite —
[`examples/evolution/`](../../examples/evolution/README.md): pendulum
(continuous dynamics + energy guarantee), bouncing ball (hybrid events), heat
diffusion (fields evolve too), spring-mass control, and Lorenz. Every console
example is self-checking: it verifies a physical guarantee about its own
evolution and exits nonzero if the guarantee fails.

Each file opens with a "North-star" comment showing how the same system will
read in the aspirational `flow { evolves as }` syntax —
[VISION.md](../../VISION.md) and
[docs/vision/north-star.md](../vision/north-star.md) map the road from here
to there.

---

## Exercises

### Exercise 1: Stiffer Spring

In `spring_mass_control.flow`, change the spring constant (the `-1.0` in the
`A` row) to `-4.0`. Does the GA still stabilize the loop? What happens to
`rho_cl`?

### Exercise 2: Unreachable State

Set `B 0.0 0.0` in a `dsys` block and check `controllable` in a `sense`
block. Why must it report 0?

### Exercise 3: Chaos Detector

Using `lyapunov_proxy` from
[`stdlib/dynamics/attractor.flow`](../library/dynamics.md#attractorflow),
compare the separation exponent of the Lorenz system (`sys_id 1`) against the
damped oscillator (`sys_id 0`). Which is positive, and what does that mean?

---

## Reference

- [Dynamics DSL reference](../language/dynamics-dsl.md)
- [Dynamics library API](../library/dynamics.md)
- [Vision](../vision.md) · [North-star grammar plan](../vision/north-star.md)
- [Language Specification](../LANGUAGE_SPEC.md)
