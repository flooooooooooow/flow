# Evolution suite

Thirty-four programs about systems that change over time. In each one the
dynamics are *declared*, not hand-integrated.

```flow
flow Pendulum {
    state angle: f64 = 0.5
    state velocity: f64 = 0.0
    param damping: f64 = 0.3

    angle evolves as velocity
    velocity evolves as -9.81 * sin(angle) - damping * velocity
}
```

The integrator is generated. A reset is a first-class event
(`when height reaches 0.0 { velocity becomes -0.8 * velocity }`), not an `if`
buried in a loop. The same source lowers to C and to MLIR.

Every example prints a measured quantity checked against theory and exits
nonzero if the check fails, so the suite doubles as a regression test.

```bash
./flow run examples/evolution/<name>.flow          # console programs
./flow gfx examples/evolution/lorenz_gfx.flow      # the one windowed demo
```

## Classic dynamics

| Example | What it demonstrates, and the check |
|---|---|
| `duffing.flow` | Forced chaotic oscillator; Poincaré section |
| `van_der_pol.flow` | Relaxation oscillation; period against the large-mu asymptotic |
| `rossler.flow` | Rössler attractor; Lyapunov exponent |
| `lorenz_gfx.flow` | Lorenz attractor traced live through an RK4 solver |
| `double_pendulum.flow` | Chaos with energy drift as the integrator's own report card |
| `spring_chain.flow` | Normal modes against the analytic eigenvalues |
| `pendulum.flow` · `pendulum_rk4.flow` · `pendulum_evolves.flow` | The same pendulum by hand, by RK4, and by `evolves as` |
| `pendulum_always.flow` | An `always` constraint holding over the trajectory |
| `pendulum_represent_linear.flow` | Small-angle linearisation via `represent linear` |
| `units_kinematics.flow` | Units of measure checked at compile time |

## Hybrid and event-driven

| Example | What it demonstrates, and the check |
|---|---|
| `bouncing_ball.flow` · `bouncing_ball_evolves.flow` | Zero-crossing detection and a restitution reset |
| `bouncing_ball_energy.flow` | Measured bounce heights against the geometric series |
| `thermostat_evolves.flow` · `thermostat_hysteresis.flow` | Deadband switching; measured duty cycle |
| `water_tank_cascade.flow` | Level control with overflow events |
| `traffic_lights.flow` | `every <duration>` time blocks driving a signal network |
| `pacemaker.flow` | Integrate-and-fire with a refractory period |

## Growth and populations

| Example | What it demonstrates, and the check |
|---|---|
| `logistic_bifurcation.flow` | Period doubling; the Feigenbaum constant measured |
| `lotka_volterra.flow` | Predator-prey; the conserved quantity as the check |
| `sir_epidemic.flow` | Epidemic curve; the final-size equation solved two ways |
| `chemostat.flow` | Monod steady states and the washout threshold |
| `age_structured.flow` | Leslie matrix; three routes to one dominant eigenvalue |
| `heat_diffusion.flow` | A field evolving: 1D heat equation over a rod |

## Control and composition

| Example | What it demonstrates, and the check |
|---|---|
| `spring_mass_control.flow` | Model, analyse, control in one file via `dsys` |
| `spring_mass_lqr.flow` · `chain4_lqr.flow` | LQR gains derived in Flow |
| `pid_tuning.flow` | Ziegler-Nichols on 1/(s+1)^3; Ku = 8, Tu = 2pi/sqrt(3) |
| `cruise_control.flow` | PI pole placement; I-P overshoot matches the damping formula |
| `robot_connect.flow` · `parent_input_connect.flow` | `connect` composing subsystems |
| `flow_pipeline_stages.flow` | A `flow` block as one stage of a `\|>` pipeline |

## Related

[Morphogenesis gallery](morphogenesis.md) · [Game gallery](games.md) ·
[Example Atlas](../project/example-atlas.md) ·
[dynamics DSL](../language/dynamics-dsl.md) · [VISION](../VISION.md)
