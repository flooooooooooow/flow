# 7. From update loops to flows

A changing system keeps state and updates it over time. An ordinary loop can
do this. A `flow` declaration states the equations and generates the
integration code.

## 7.1 Discrete state

Consider exponential decay:

```text
dy/dt = -k y
```

For a time step `dt`, explicit Euler gives:

```text
y_next = y + (-k y) dt
```

The direct Flow program is:

```flow
let rate: f64 = 0.8
let dt: f64 = 0.1
let mut amount: f64 = 10.0

for step in 0 to 10 {
    amount = amount + (0.0 - rate * amount) * dt
}
```

Three categories are visible:

| Category | Values |
|---|---|
| Fixed parameters | `rate`, `dt` |
| State | `amount` |
| Evolution rule | `amount + (-rate * amount) * dt` |

## 7.2 Complete Euler demonstration

```flow
extern {
    function printf(fmt: string, ...) -> i32
}

function main() -> i32 {
    let rate: f64 = 0.8
    let dt: f64 = 0.1
    let mut amount: f64 = 10.0

    printf("t=%.1f amount=%.6f\n", 0.0, amount)
    for step in 0 to 10 {
        amount = amount + (0.0 - rate * amount) * dt
        if step == 4 or step == 9 {
            let time: f64 = (step + 1) as f64 * dt
            printf("t=%.1f amount=%.6f\n", time, amount)
        }
    }
    return 0
}
```

Source: [`examples/book/07_decay.flow`](../../examples/book/07_decay.flow)

```bash
./flow run examples/book/07_decay.flow
```

```text
t=0.0 amount=10.000000
t=0.5 amount=6.590815
t=1.0 amount=4.343885
```

The exact continuous solution at `t = 1` is `10e^-0.8`, approximately
`4.493290`. The Euler result differs because the continuous trajectory was
replaced by ten finite steps. Reducing `dt` normally reduces this discretisation
error at the cost of more updates.

## 7.3 Declaring evolution

The same relation can be stated as a flow:

```flow
flow Decay {
    state amount: f64 = 10.0
    param rate: f64 = 0.8

    amount evolves as 0.0 - rate * amount
}
```

The right-hand side is the derivative, not the next value. Conceptually, the
compiler generates state storage and a step operation. The integrator evaluates
the derivative and advances the stored state.

Use the Python compiler host for full evolution syntax:

```bash
FLOW_HOST=python ./flow run model.flow
```

## 7.4 Coupled state: a pendulum

A damped pendulum has two state variables:

```flow
flow Pendulum {
    state angle: f64 = 2.0
    state velocity: f64 = 0.0

    param gravity: f64 = 9.81
    param length: f64 = 1.0
    param damping: f64 = 0.5

    angle evolves as velocity
    velocity evolves as -(gravity / length) * sin(angle)
                        - damping * velocity
}
```

The equations are simultaneous. The derivative of `angle` depends on
`velocity`; the derivative of `velocity` depends on both current state values.
An integrator must evaluate a consistent state snapshot for a step. Sequentially
assigning `angle` and then using the updated angle for `velocity` would describe
a different numerical scheme.

Run the repository's complete pendulum demonstration:

```bash
FLOW_HOST=python ./flow run examples/evolution/pendulum_evolves.flow
```

Its table reports time, angle, velocity, and mechanical energy. With positive
damping, the reported energy decreases and the pendulum approaches rest.

## 7.5 Integrator choice

The evolution rule and the integration method are separate concerns. A solver
block can request a method and time step:

```text
solver {
    dt 5 ms
    method rk4
}
```

Euler uses one derivative estimate per step. Classical fourth-order
Runge–Kutta uses four estimates and combines them. RK4 usually provides much
smaller error for smooth systems at the same `dt`, but each step costs more.

Run the RK4 pendulum:

```bash
FLOW_HOST=python ./flow run examples/evolution/pendulum_rk4.flow
```

## 7.6 Model checks

A simulation should test properties as well as produce values. Useful checks
include:

- a conserved quantity remains within a numeric tolerance;
- a damped energy does not increase beyond a tolerance;
- a population or concentration remains nonnegative;
- a controller settles inside a specified band by a specified time;
- reducing `dt` changes the reported result by less than an accepted amount.

For the decay model, a simple bounded check is:

```text
if amount < 0.0 or amount > 10.0 {
    return 1
}
```

Such a check does not prove the differential equation correct. It detects a violation
of one required property in the executed numerical scheme.

## 7.7 State, parameters, and inputs

Keep the categories distinct:

- **state** persists and is advanced by the solver;
- **parameters** configure the model and remain fixed during an ordinary run;
- **inputs** are supplied by another system or function over time;
- **derived values** are computed from the current state and need not be stored.

Storing every derived value as state enlarges the system and creates additional
consistency obligations. Store only quantities with independent evolution.

## Exercises

1. Run the Euler decay model with `dt = 0.05` for twenty steps. Compare the
   result at `t = 1` with the ten-step result.
2. Add a nonnegative-state check after every Euler update.
3. Express the two-state system `dx/dt = v`, `dv/dt = -4x - 0.2v` as a flow.
4. Identify the state, parameters, and derived energy of that system.
5. Compare the output of the Euler and RK4 pendulum demonstrations.

Return to the [book contents](README.md).
