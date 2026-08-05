# examples/evolution — the vision, running today

Flow's founding idea ([VISION.md](../../VISION.md)) is that programs describe
**systems that evolve through time** — state, dynamics, events, analysis, and
guarantees in one language. Prefer the declarative `flow` / `evolves as` /
`when` / `always` / `solver` surface. Hand-rolled integrators remain only as
pedagogical “how it lowers” companions.

Every console example is self-checking: it verifies a physical guarantee about
its own evolution and exits nonzero if the guarantee fails.

## Canonical (start here)

| Example | Pattern | What it shows |
|---|---|---|
| [`pendulum_evolves.flow`](pendulum_evolves.flow) | `flow` + `evolves as` | Nonlinear damped pendulum (Euler `_step`) |
| [`pendulum_rk4.flow`](pendulum_rk4.flow) | `solver { method rk4 }` | Same plant, classic RK4 in `_step` |
| [`pendulum_always.flow`](pendulum_always.flow) | `always { … }` | Runtime invariant on angle |
| [`bouncing_ball_evolves.flow`](bouncing_ball_evolves.flow) | `when … reaches` | Hybrid bounce with restitution |
| [`robot_connect.flow`](robot_connect.flow) | `connect { … }` | Nested plant + controller wiring |
| [`pendulum_represent_linear.flow`](pendulum_represent_linear.flow) | `represent linear` | Bridge to `dsys` analysis |
| [`spring_mass_control.flow`](spring_mass_control.flow) | `dsys` / `sense` / `ga` / `closed` | Model → analyze → control |
| [`lorenz_gfx.flow`](lorenz_gfx.flow) | `flow` + `gfx_frame_pump` | Live Lorenz trail in a window |
| [`heat_diffusion.flow`](heat_diffusion.flow) | field Euler (stdlib PDE later) | 1D heat + ASCII frames |

```
./flow run examples/evolution/pendulum_evolves.flow
./flow run examples/evolution/pendulum_rk4.flow
./flow run examples/evolution/bouncing_ball_evolves.flow
./flow gfx examples/evolution/lorenz_gfx.flow
```

## Pedagogical (hand integration)

These reimplement the same physics with explicit RK4 / event math so you can
see what the declarative forms lower toward. Prefer the canonical files above
for demos and docs.

| Example | Prefer instead |
|---|---|
| [`pendulum.flow`](pendulum.flow) | `pendulum_evolves.flow` / `pendulum_rk4.flow` |
| [`bouncing_ball.flow`](bouncing_ball.flow) | `bouncing_ball_evolves.flow` |

## Quick tours

### `pendulum_evolves.flow` — continuous dynamics

```
./flow run examples/evolution/pendulum_evolves.flow
```

```
      t [s]  angle [rad]   vel [rad/s]  energy [J]
    -------  -----------  ------------  ----------
       0.00       2.0000        0.0000     13.8924
       ...
    OK: energy decreased monotonically, pendulum settled at rest
```

### `bouncing_ball_evolves.flow` — hybrid systems

```
./flow run examples/evolution/bouncing_ball_evolves.flow
```

### `spring_mass_control.flow` — model, analyze, control

```
./flow run examples/evolution/spring_mass_control.flow
```

### `lorenz_gfx.flow` — live simulation

```
./flow gfx examples/evolution/lorenz_gfx.flow
```

`flow Lorenz` + `solver { method rk4 }` drives the attractor; `gfx_frame_pump`
handles poll / Esc / close.

## Verifying the suite

```
./flow run examples/evolution/pendulum_evolves.flow
./flow run examples/evolution/bouncing_ball_evolves.flow
python3 -m flow.transpiler examples/evolution/lorenz_gfx.flow --c --lenient -o /tmp/out.c
```
