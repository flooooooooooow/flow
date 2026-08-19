# 7. From update loops to flows

A changing system keeps state and updates it over time. An ordinary loop can do this; a `flow` declaration states the evolution equations and lets the compiler generate stepping code. Every `flow` block in this chapter is compiler-checked in CI.

## 7.1 Explicit Euler in ordinary Flow

For `dy/dt = -k y`, an explicit Euler step is `y_next = y + (-k y) dt`.

```flow
function decay_steps() -> f64 {
    let rate: f64 = 0.8
    let dt: f64 = 0.1
    let mut amount: f64 = 10.0

    for step in 0 to 10 {
        amount = amount + (0.0 - rate * amount) * dt
    }
    return amount
}
```

The fixed parameters are `rate` and `dt`; `amount` is state; the assignment is the evolution rule.

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
FLOW_HOST=python ./flow run examples/book/07_decay.flow
```

## 7.3 Declaring evolution

The same relation can be stated directly:

```flow
flow Decay {
    state amount: f64 = 10.0
    param rate: f64 = 0.8

    amount evolves as 0.0 - rate * amount
}
```

The right-hand side is a derivative, not the next value. The compiler generates state storage, a derivative function, and `Decay_step`.

## 7.4 Coupled state: a pendulum

```flow
extern {
    function sin(x: f64) -> f64
}

flow PendulumBook {
    state angle: f64 = 2.0
    state velocity: f64 = 0.0
    param gravity: f64 = 9.81
    param length: f64 = 1.0
    param damping: f64 = 0.5

    angle evolves as velocity
    velocity evolves as -(gravity / length) * sin(angle) - damping * velocity
}
```

All derivatives are evaluated from a consistent pre-step state. Run the complete repository example with:

```bash
FLOW_HOST=python ./flow run examples/evolution/pendulum_evolves.flow
```

## 7.5 Solver choice

The model and numerical integration method are separate concerns. Solver selection belongs inside the `flow` declaration:

```flow
flow Rk4Decay {
    state amount: f64 = 10.0
    param rate: f64 = 0.8

    solver { dt 5 ms method rk4 }
    amount evolves as 0.0 - rate * amount
}
```

The checked-in RK4 pendulum is [`examples/evolution/pendulum_rk4.flow`](../../examples/evolution/pendulum_rk4.flow).

## 7.6 Model checks

A simulation should test properties as well as produce values. A bounded-state check can be an ordinary function:

```flow
function valid_amount(amount: f64) -> bool {
    if amount < 0.0 or amount > 10.0 {
        return false
    }
    return true
}
```

Useful checks include conserved quantities, monotonic dissipated energy, nonnegative concentrations, settling bands, and convergence as `dt` is reduced.

## 7.7 State, parameters, inputs, and derived values

State persists and is advanced by the solver. Parameters configure the model. Inputs are supplied from outside the model. Derived values are computed from current state and usually should not be stored as independent state.

## Exercises

Run the Euler decay with half the step size; add a nonnegative-state check; express `dx/dt = v`, `dv/dt = -4x - 0.2v` as a `flow`; identify its state and derived energy; then compare Euler and RK4 results.

Return to the [book contents](README.md).
