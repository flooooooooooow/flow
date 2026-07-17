# examples/evolution — the vision, running today

Flow's founding idea ([VISION.md](../../VISION.md)) is that programs describe
**systems that evolve through time** — state, dynamics, events, analysis, and
guarantees in one language. These five examples are the flagship suite for that
vision, written in *today's* Flow. Each file opens with a "North-star" comment
showing how the same system will read in the aspirational VISION.md syntax.

Every console example is self-checking: it verifies a physical guarantee about
its own evolution and exits nonzero if the guarantee fails.

| Example | VISION.md pillar | What it shows |
|---|---|---|
| [`pendulum.flow`](pendulum.flow) | Continuous dynamics (`evolves as`) | Nonlinear damped pendulum, RK4, energy guarantee |
| [`bouncing_ball.flow`](bouncing_ball.flow) | Hybrid systems (`when h reaches 0`) | Event detection + restitution reset, exact impact times |
| [`spring_mass_control.flow`](spring_mass_control.flow) | Model → analyze → control | `dsys` plant, `sense`, `ga evolve`, `closed` in one file |
| [`heat_diffusion.flow`](heat_diffusion.flow) | Fields / scientific computing | 1D heat equation, ASCII heat-map frames, decay guarantee |
| [`lorenz_gfx.flow`](lorenz_gfx.flow) | Live simulation / digital twins | Lorenz attractor in a real window, fading trail |

## 1. `pendulum.flow` — continuous dynamics

The VISION.md anchor: `theta'' = -(g/L) sin(theta) - c theta'`, integrated with
RK4. Prints the trajectory and **verifies** that damped energy is monotonically
non-increasing and the pendulum settles at equilibrium.

```
./flow run examples/evolution/pendulum.flow
```

```
      t [s]  angle [rad]   vel [rad/s]  energy [J]
    -------  -----------  ------------  ----------
       0.00       2.0000        0.0000     13.8924
       2.00       0.4831        2.8760      5.2583
       ...
      24.00      -0.0021        0.0129      0.0001

    OK: energy decreased monotonically, pendulum settled at rest
```

## 2. `bouncing_ball.flow` — hybrid systems

Continuous ballistic flight punctuated by discrete impact events. The zero
crossing is solved *inside* the step, so measured impact times match the
closed-form bounce schedule to ~1e-13 s. Restitution reset:
`velocity becomes -0.8 * velocity`.

```
./flow run examples/evolution/bouncing_ball.flow
```

```
    bounce   impact t [s]   analytic t [s]   |dt| [s]    rebound apex [m]
    ------   ------------   --------------   ---------   ----------------
         1       0.638551         0.638551    4.66e-15           1.280000
         2       1.660232         1.660232    6.02e-14           0.819200
       ...
        10       5.061319         5.061319    1.33e-14           0.023058

    OK: 10 decaying bounces, impact times match closed form
```

## 3. `spring_mass_control.flow` — model, analyze, control

One file, whole workflow, using the `dsys` declarative surface syntax
(pre-parse expander, `src/flow/dynamics_dsl.py`): a continuous mass-spring-
damper plant that the compiler discretizes, a `sense` block proving
controllability and measuring the open-loop spectral radius, a `ga evolve`
block searching feedback gains, and a `closed` block certifying stability —
then an open- vs closed-loop release comparison.

```
./flow run examples/evolution/spring_mass_control.flow
```

```
    controllable          : yes
    open-loop  rho(A)     : 0.9950   (lightly damped ringing)
    evolved gains         : k1 = 2.0310,  k2 = 3.0894
    closed-loop rho(A-BK) : 0.8375
      t [s]    open x [m]   closed x [m]
        3.0       -0.8403         0.0103
        6.0        0.6922        -0.0001

    OK: controllable plant, stable evolved loop, faster settling
```

## 4. `heat_diffusion.flow` — fields evolve too

The 1D heat equation on a 32-cell rod, explicit Euler at r = 0.4 (stable),
rendered as ASCII heat-map frames. Verifies excess heat decays monotonically
toward ambient and no cell goes NaN.

```
./flow run examples/evolution/heat_diffusion.flow
```

```
    t=   0.0  |              @@@@              |  q= 320.00
    t=  16.0  |  ...::---===++++++===---::...  |  q= 315.59
    t=  96.0  |  ...::::::::------::::::::...  |  q= 150.71
    t= 256.0  |      ....................      |  q=  29.09

    OK: field diffused, excess heat decayed monotonically
```

## 5. `lorenz_gfx.flow` — live simulation

The first Flow example to combine the dynamics stdlib and the graphics stdlib:
the Lorenz attractor stepped by `rk4_step_n`, its (x, z) plane drawn into a
real window as a fading 320-point comet trail (brighter = newer). Bounded to
2000 frames; Esc or closing the window exits early.

```
./flow gfx examples/evolution/lorenz_gfx.flow
```

## Verifying the suite

All five transpile strictly and pass the same compile check as CI:

```
python3 -m flow.transpiler examples/evolution/<file> --c --lenient -o /tmp/out.c
clang -fsyntax-only -Wno-everything /tmp/out.c
```
