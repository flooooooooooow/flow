# FLOW Tutorial: Dynamics

Modeling systems that evolve through time, from a hand-written integrator to
Flow's declarative `dsys` syntax, analysis, and evolved control. This is the
tutorial for Flow's founding thesis ([VISION.md](../../VISION.md)): programs as
descriptions of **evolution**, not instruction sequences.

For the shipped `flow` / `evolves as` / `field` syntax itself, see
[evolution.md](evolution.md). This track focuses on integrators, state-space
systems, and the `dsys` → `sense` → `ga evolve` / LQR control path.

Prerequisites: [intermediate.md](intermediate.md) (structs, arrays, `ptr<f64>`).

## Part 1: An ODE Integrator by Hand

Every dynamical program starts from the same loop: state, a derivative, a time
step. Explicit Euler for exponential decay `dy/dt = -y`:

### 1.1 Explicit Euler

```flow
function euler_step(y: f64, dt: f64) -> f64 {
    let dy: f64 = 0.0 - y
    return y + dt * dy
}

function main() -> i32 {
    let mut y: f64 = 1.0
    let dt: f64 = 0.1
    for k in 0 to 10 {
        y = euler_step(y, dt)
    }
    printf("y(1.0) ≈ %f (exact e^-1 ≈ 0.3679)\n", y)
    return 0
}
```

Euler drifts; the classic fix is Runge-Kutta 4. Both, plus a midpoint method
and accuracy comparisons against closed-form solutions, live in
[`examples/numerical/ode_solver.flow`](../../examples/numerical/ode_solver.flow):

```bash
./flow run examples/numerical/ode_solver.flow
```

### 1.2 Hybrid bounce (hand-written event)

A bouncing ball is continuous flight punctuated by discrete impacts. Detect
the floor crossing inside the step, then flip velocity:

```flow
function main() -> i32 {
    let gravity: f64 = 9.81
    let restitution: f64 = 0.8
    let dt: f64 = 0.01
    let mut h: f64 = 2.0
    let mut v: f64 = 0.0
    let mut bounces: i32 = 0
    for k in 0 to 400 {
        v = v - gravity * dt
        h = h + v * dt
        if h <= 0.0 {
            if v < 0.0 {
                h = 0.0
                v = 0.0 - restitution * v
                bounces = bounces + 1
            }
        }
    }
    printf("bounces=%d final_h=%f\n", bounces, h)
    return 0
}
```

The declarative form of the same system uses `when height reaches 0.0`, see
[evolution.md](evolution.md) and
[`bouncing_ball_evolves.flow`](../../examples/evolution/bouncing_ball_evolves.flow).

---

## Part 2: State-Space Systems with `stdlib/dynamics`

Hand loops don't compose. The dynamics library gives you a first-class system
type, matrices over caller-provided buffers, no allocation:

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

Discretize it and ask a structural question, *can inputs steer every state?*

```flow
let sys: DynamicalSystem = dsys_euler_discretize(cont, Ad, Bd, Id, sc)

let ok: i32 = is_controllable(sys, c1, c2, c3, c4, c5)   # rank of [B, AB]
```

(The extra arguments are scratch buffers, `array<f64, 4>` each. See the
[library reference](../library/dynamics.md#state_spaceflow) for every
signature.) Run the full version:

```bash
./flow run examples/dynamics/controllability_demo.flow
```

`state_step` advances one step, `rollout_discrete` simulates a whole
trajectory, and [`gramian.flow`](../library/dynamics.md#gramianflow) measures
*how much* input energy it takes to reach states, not just whether you can.

### 2.1 Discrete double-integrator step (browser)

A tiny discrete plant `x' = x + v·dt`, `v' = v + u·dt` you can step by hand:

```flow
function main() -> i32 {
    let dt: f64 = 0.1
    let mut x: f64 = 0.0
    let mut v: f64 = 0.0
    let u: f64 = 1.0
    for k in 0 to 10 {
        x = x + v * dt
        v = v + u * dt
    }
    printf("after 1s: x=%f v=%f\n", x, v)
    return 0
}
```

---

## Part 3: The `dsys` Surface Syntax

All that buffer plumbing disappears with the declarative
[dynamics DSL](../language/dynamics-dsl.md), a pre-parse expander that turns
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

> [!note] Native only
> `dsys` / `sense` / `ga evolve` / `analyze { lqr }` expand at compile time.
> Run them with `./flow run`, the browser interpreter does not expand the DSL.

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

`rho_open >= 1` means the discrete plant does not decay on its own, the
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

For everything at once, including a `GAAnalysisReport` struct with baseline
vs evolved cost and convergence generation, use the one-shot form:

```flow
analyze plant ga k1 k2 over rollout -> report { full }
```

### 5.1 Discrete LQR (shipped)

Prefer optimal gains over a GA search when the plant is linear and small
(`n ≤ 8`). Same spring-mass plant, gains from `analyze { lqr }`:

```bash
./flow run examples/evolution/spring_mass_lqr.flow
./flow run examples/evolution/chain4_lqr.flow
```

```flow
dsys plant {
    continuous
    dt 0.1
    n 2 m 1 p 1
    A 0.0 1.0 -1.0 -0.2
    B 0.0 1.0
    C 1.0 0.0
}

analyze plant {
    lqr {
        Q 10.0 1.0
        R 0.1
        -> k1 k2
    }
}
```

See [Dynamics library](../library/dynamics.md) for the full API.

### 5.2 PD feedback sketch (browser)

A one-dimensional “plant” with proportional-derivative feedback you can tune
interactively in the browser:

```flow
function main() -> i32 {
    let dt: f64 = 0.05
    let kp: f64 = 4.0
    let kd: f64 = 1.5
    let target: f64 = 1.0
    let mut x: f64 = 0.0
    let mut v: f64 = 0.0
    for k in 0 to 40 {
        let err: f64 = target - x
        let u: f64 = kp * err - kd * v
        v = v + u * dt
        x = x + v * dt
    }
    printf("settled x=%f v=%f\n", x, v)
    return 0
}
```

### 5.3 Open-loop ring (browser)

```flow
function main() -> i32 {
    let dt: f64 = 0.1
    let mut x: f64 = 1.0
    let mut v: f64 = 0.0
    for k in 0 to 40 {
        let a: f64 = -1.0 * x - 0.2 * v
        v = v + a * dt
        x = x + v * dt
    }
    printf("x=%f v=%f\n", x, v)
    return 0
}
```

### 5.4 Controllability intuition (browser)

```flow
function main() -> i32 {
    # rank idea: with B=[0,1], we can change v directly, then x via integration
    let can_steer_v: i32 = 1
    let can_steer_x: i32 = can_steer_v
    printf("controllable_sketch=%d\n", can_steer_x)
    return 0
}
```

### 5.5 Rollout cost (browser)

```flow
function main() -> i32 {
    let mut cost: f64 = 0.0
    let mut x: f64 = 1.0
    let mut v: f64 = 0.0
    let dt: f64 = 0.1
    let k1: f64 = 2.0
    let k2: f64 = 3.0
    for t in 0 to 30 {
        let u: f64 = 0.0 - k1 * x - k2 * v
        cost = cost + x * x + 0.1 * u * u
        let a: f64 = -1.0 * x - 0.2 * v + u
        v = v + a * dt
        x = x + v * dt
    }
    printf("cost=%f\n", cost)
    return 0
}
```

---

## Part 6: Where to Go Next

1. **Declarative evolution**, [evolution.md](evolution.md): `flow` /
   `evolves as`, hybrid events, `always`, phase portraits, `field` PDE.
2. **Live chaos**, Lorenz attractor in a native window:

```bash
./flow gfx examples/evolution/lorenz_gfx.flow
```

![Lorenz attractor](../demos/lorenz.gif)

3. **Flagship suite**, [`examples/evolution/`](../../examples/evolution/README.md):
   pendulum, bouncing ball, heat diffusion, spring-mass control, LQR, Lorenz.
   Every console example is self-checking.

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

### Exercise 4: LQR vs GA

Compare `spring_mass_lqr.flow` gains to the GA gains from
`spring_mass_control.flow`. Which settles faster for the same initial
condition `[1, 0]`?

---

## Reference

- [Evolution tutorial](evolution.md), `flow` / `evolves` / `field`
- [Dynamics DSL reference](../language/dynamics-dsl.md)
- [Dynamics library API](../library/dynamics.md)
- [Vision](../vision.md) · [North-star grammar](../vision/north-star.md)
- [Language Specification](../LANGUAGE_SPEC.md)
