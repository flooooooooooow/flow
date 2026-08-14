# 13. Evolution, hybrid systems, dynamics, and fields

Chapter 7 introduced continuous state. Flow also supports solver settings,
inputs and outputs, sampled actions, hybrid events, invariants, composed
models, state-space analysis, controller synthesis, and field equations.

All forms below use the Python compiler host.

## 13.1 Generated flow interface

```flow
flow Motor {
    state speed: f64 = 0.0
    input voltage: f64
    output measured: f64 = speed
    param damping: f64 = 0.5

    speed evolves as voltage - damping * speed
}
```

The expander generates a state struct, `Motor_new()`, and
`Motor_step(ptr<Motor>, dt)`. State persists; parameters configure the model;
inputs are assigned by an embedding system; outputs derive an exposed value.

## 13.2 Solver declaration

```flow
solver {
    dt 1 ms
    method rk4
}
```

Supported evolution examples use explicit Euler or RK4. Euler is inexpensive
and first order. RK4 evaluates four derivative stages and is fourth order for
smooth problems. A solver setting does not replace stability analysis: a
method may still be unsuitable for a stiff equation or excessive time step.

## 13.3 Worked solver: one RK4 step

RK4 evaluates the derivative four times. The intermediate values estimate the
slope at the start, twice near the middle, and at the end of the step.

```flow
function derivative(value: f64, rate: f64) -> f64 {
    return 0.0 - rate * value
}

function rk4_step(value: f64, rate: f64, dt: f64) -> f64 {
    let k1: f64 = derivative(value, rate)
    let k2: f64 = derivative(value + 0.5 * dt * k1, rate)
    let k3: f64 = derivative(value + 0.5 * dt * k2, rate)
    let k4: f64 = derivative(value + dt * k3, rate)

    return value
        + dt * (k1 + 2.0 * k2 + 2.0 * k3 + k4) / 6.0
}
```

Ten steps of size `0.1` advance the model from `t = 0` to `t = 1`:

```flow
let rate: f64 = 0.8
let dt: f64 = 0.1
let mut value: f64 = 10.0

for step in 0 to 10 {
    value = rk4_step(value, rate, dt)
}
```

Source:
[`examples/book/13_rk4_decay.flow`](../../examples/book/13_rk4_decay.flow)

```bash
./flow run examples/book/13_rk4_decay.flow
```

```text
rk4 value: 4.493291
```

The exact value is `10e^-0.8`, about `4.493290`. The example accepts a narrow
interval around that value and returns failure if the result leaves it.

## 13.4 Sampled actions

Discrete updates can coexist with continuous equations:

```flow
every 1 ms {
    command becomes kp * (setpoint - feedback)
}
```

`becomes` assigns discrete state. `every` sets the sample period. The plant is
integrated continuously, while the controller runs at fixed intervals.

## 13.5 Hybrid events

```flow
flow Ball {
    state height: f64 = 2.0
    state velocity: f64 = 0.0
    param gravity: f64 = 9.81
    param restitution: f64 = 0.8

    height evolves as velocity
    velocity evolves as -gravity

    when height reaches 0.0 {
        velocity becomes -restitution * velocity
        height becomes 0.0
    }
}
```

`reaches` detects a threshold crossing at the integrator's event resolution
and applies a discrete reset. Event timing therefore has a time-step error even
when the continuous integrator is otherwise accurate.

The energy-ledger demonstration compares simulated apexes, flight times,
energy loss, and the Zeno horizon with closed forms:

```bash
FLOW_HOST=python ./flow run examples/evolution/bouncing_ball_energy.flow
```

## 13.6 Invariants

```flow
always {
    angle < 3.15
    angle > -3.15
}
```

`always` emits runtime checks after state updates. It catches an observed
violation; it is not a proof over every real time between numeric samples.

```bash
FLOW_HOST=python ./flow run examples/evolution/pendulum_always.flow
```

## 13.7 Flow composition

```flow
flow Robot {
    plant: Motor
    controller: Controller

    connect {
        controller.command -> plant.voltage
        plant.measured -> controller.feedback
    }
}
```

Connections are topologically ordered and child flows are stepped through the
parent. Feedback must be broken by state; a pure combinational algebraic loop
is rejected or needs an algebraic-loop solver, which is not supplied.
Unconnected child inputs are assigned by the embedder.

```bash
FLOW_HOST=python ./flow run examples/evolution/robot_connect.flow
```

## 13.8 Representations

`represent phase_portrait` produces a drawing-oriented representation used by
graphics demonstrations. `represent linear` attaches an explicit local linear
model to a nonlinear flow:

```flow
represent linear {
    at (angle: 0.0, velocity: 0.0)
    inputs (torque)
    outputs (angle)
    continuous
    dt 0.01
    n 2 m 1 p 1
    A 0.0 1.0 -9.81 -0.1
    B 0.0 1.0
    C 1.0 0.0
}
```

The coefficients must currently be supplied. Automatic Jacobian evaluation at
an equilibrium is not implemented.

```bash
FLOW_HOST=python ./flow run examples/evolution/pendulum_represent_linear.flow
```

## 13.9 State-space systems

The dynamics DSL describes a plant with matrices and timing:

```flow
dsys plant {
    continuous
    dt 0.01
    n 2 m 1 p 1
    A 0.0 1.0 -2.0 -0.3
    B 0.0 1.0
    C 1.0 0.0
}
```

The expander builds an ordinary Flow representation using
`stdlib/dynamics`. Continuous models can be discretised for analysis and
simulation.

## 13.10 Analysis and control

```flow
sense on plant {
    controllable -> can_control
    observable -> can_observe
    spectral -> radius
}
```

Analysis includes controllability, observability, spectral information,
simulation, frequency response, and associated reports where the selected
system shape permits them.

Discrete LQR computes state feedback from `A`, `B`, `Q`, and `R`. A genetic
algorithm can search controller parameters and score them over a rollout:

```flow
analyze plant ga k1 k2 over rollout -> report { full }
```

```bash
FLOW_HOST=python ./flow run examples/dynamics/ga_dsys_syntax.flow
FLOW_HOST=python ./flow run examples/evolution/spring_mass_lqr.flow
```

The [dynamics tutorial](../tutorials/dynamics.md) lists the available examples
and report forms.

## 13.11 Field equations

```flow
field T: f64[32] on Line
T evolves as laplacian(T)
boundary T { left = 20.0  right = 20.0 }
```

The field expander generates storage and a finite-difference update. For the
one-dimensional explicit heat equation, the nondimensional step ratio must
satisfy its stability condition; the demonstration uses `r = 0.4` with the
common `r <= 0.5` bound.

```bash
FLOW_HOST=python ./flow run examples/evolution/heat_diffusion.flow
```

Fields are numerical grids, not symbolic PDE proofs. Model validation must
still cover grid resolution, boundary consistency, truncation error,
stability, and convergence.

## 13.12 Validation practice

For any evolving model, record:

- dimensions and units;
- initial conditions and parameter values;
- solver method and time step;
- conserved, dissipated, or bounded quantities;
- event tolerances;
- a time-step refinement comparison;
- a reference solution or independent implementation where available.

## Exercises

1. Add a sampled proportional controller to a first-order plant.
2. State the energy change expected at a bouncing-ball reset.
3. Supply a linear representation for a mass-spring-damper flow.
4. Vary the heat-equation step ratio across the stability boundary.

Next: [Numerics, automatic differentiation, and machine learning](14-numerics-autodiff-and-ml.md).
