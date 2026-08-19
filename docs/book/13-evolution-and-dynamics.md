# 13. Evolution, hybrid systems, dynamics, and fields

Flow supports language-level evolution, solver settings, sampled actions, hybrid events, state-space analysis, controller search, and field equations. Every `flow` block in this chapter is compiler-checked in CI.

Use the full compiler host for the complete evolution surface:

```bash
FLOW_HOST=python ./flow run file.flow
```

## 13.1 Generated flow interface

```flow
flow MotorBook {
    state speed: f64 = 0.0
    input voltage: f64
    output measured: f64 = speed
    param damping: f64 = 0.5

    speed evolves as voltage - damping * speed
}
```

The compiler generates a state representation, `MotorBook_new()`, and `MotorBook_step(ptr<MotorBook>, dt)`.

## 13.2 Solver declaration

Solver configuration belongs inside the model:

```flow
flow Rk4Model {
    state value: f64 = 1.0
    param rate: f64 = 0.5

    solver { dt 1 ms method rk4 }
    value evolves as -rate * value
}
```

Euler and RK4 are both exercised by checked-in examples. Solver choice does not replace numerical stability analysis.

## 13.3 RK4 as ordinary Flow

```flow
function derivative(value: f64, rate: f64) -> f64 {
    return 0.0 - rate * value
}

function rk4_step(value: f64, rate: f64, dt: f64) -> f64 {
    let k1: f64 = derivative(value, rate)
    let k2: f64 = derivative(value + 0.5 * dt * k1, rate)
    let k3: f64 = derivative(value + 0.5 * dt * k2, rate)
    let k4: f64 = derivative(value + dt * k3, rate)
    return value + dt * (k1 + 2.0 * k2 + 2.0 * k3 + k4) / 6.0
}

function ten_steps() -> f64 {
    let rate: f64 = 0.8
    let dt: f64 = 0.1
    let mut value: f64 = 10.0
    for step in 0 to 10 {
        value = rk4_step(value, rate, dt)
    }
    return value
}
```

The checked-in demonstration is [`examples/book/13_rk4_decay.flow`](../../examples/book/13_rk4_decay.flow).

## 13.4 Sampled actions

Discrete `becomes` updates can coexist with continuous equations:

```flow
flow SampledController {
    state command: f64 = 0.0
    input setpoint: f64
    input feedback: f64
    param kp: f64 = 2.0

    every 1 ms {
        command becomes kp * (setpoint - feedback)
    }
}
```

`every` establishes the sample interval for the discrete action.

## 13.5 Hybrid events

```flow
flow BallBook {
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

The event fires when the threshold crossing is detected at the integrator's event resolution, then applies the reset.

## 13.6 Runtime invariants

An `always` block is an observed runtime invariant, not a symbolic proof over continuous time:

```flow
flow BoundedAngle {
    state angle: f64 = 0.0
    state velocity: f64 = 0.0

    angle evolves as velocity
    velocity evolves as -angle

    always {
        angle < 3.15
        angle > -3.15
    }
}
```

See [`examples/evolution/pendulum_always.flow`](../../examples/evolution/pendulum_always.flow).

## 13.7 Flow composition

Composition has enough surrounding structure that the canonical source is the complete executable example [`examples/evolution/robot_connect.flow`](../../examples/evolution/robot_connect.flow). It demonstrates child flows, input/output connections, topological stepping, and the restrictions on combinational feedback.

## 13.8 Explicit linear representations

A nonlinear flow can attach an explicit local state-space model:

```flow
extern {
    function sin(x: f64) -> f64
}

flow LinearizedPendulum {
    state angle: f64 = 0.5
    state velocity: f64 = 0.0
    input torque: f64
    param gravity: f64 = 9.81
    param length: f64 = 1.0
    param damping: f64 = 0.1

    angle evolves as velocity
    velocity evolves as -(gravity / length) * sin(angle) - damping * velocity + torque

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
}
```

The coefficients are currently explicit; automatic Jacobian linearization is future work.

## 13.9 Matrix-oriented systems

```flow
dsys book_plant {
    continuous
    dt 0.01
    n 2 m 1 p 1
    A 0.0 1.0 -2.0 -0.3
    B 0.0 1.0
    C 1.0 0.0
}
```

The dynamics DSL expands to calls into `stdlib/dynamics`.

## 13.10 Analysis and controller search

A complete analysis fragment includes the plant and horizon it references:

```flow
dsys control_plant {
    discrete
    dt 0.1
    n 2 m 1 p 1
    A 1.0 0.1 0.0 1.0
    B 0.0 0.1
    C 1.0 0.0
}

horizon control_rollout finite 50

sense on control_plant {
    controllable -> can_control
    spectral -> radius
}

ga evolve on control_plant over control_rollout -> k1 k2 {
    population 8
    generations 10
    mutation 0.3
}

analyze control_plant ga ak1 ak2 over control_rollout -> report {
    full
}
```

See [Dynamics DSL](../language/dynamics-dsl.md) for the checked analysis surface.

## 13.11 Field equations

```flow
field T: f64[32] on Line
T evolves as laplacian(T)
boundary T { left = 20.0 right = 20.0 }
```

The field expander generates grid storage and finite-difference updates. The complete heat-equation example is [`examples/evolution/heat_diffusion.flow`](../../examples/evolution/heat_diffusion.flow).

## 13.12 Validation practice

For an evolving model, record dimensions and units, initial conditions, solver method, time step, bounded or conserved quantities, event tolerances, a time-step refinement comparison, and an independent reference where available.

## Exercises

Add a sampled proportional controller to a first-order plant; derive bouncing-ball energy loss at a reset; supply a linear representation for a mass-spring-damper model; and vary the heat-equation step ratio across its stability boundary.

Next: [Numerics, automatic differentiation, and machine learning](14-numerics-autodiff-and-ml.md).
