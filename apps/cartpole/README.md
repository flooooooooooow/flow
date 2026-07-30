# Cart-pole

An inverted pendulum on a cart, stabilized by state feedback. The nonlinear
model, the controllability analysis, the gain synthesis, and the closed-loop
simulation are all Flow source in this directory, compiled to native code.
The gain is computed by the program itself at startup. Every constant below
traces to a derivation in the source.

## Files

| File | Contents |
|---|---|
| `model.flow` | The plant as a `flow CartPole` block: four continuous states with `evolves as` dynamics, a force input, and two `when theta reaches` events that latch failure when the pole leaves the recoverable cone. |
| `control.flow` | Analytic linearization at the upright point, controllability rank check, and LQR gain synthesis via the discrete Riccati fixed point. Plain Flow functions over `ptr<f64>` buffers. |
| `main.flow` | Batch run: derives the gain, shows the uncontrolled pole falling, stabilizes the same plant from a 0.25 rad shove, prints the trajectory, and self-checks. Exit 0 means every check passed. |
| `cartpole_gfx.flow` | The same closed loop in a window. The pole is kicked every five seconds and caught again. Auto-exits after 1200 frames. |

## The model

Frictionless cart-pole equations from R. V. Florian, "Correct equations for
the dynamics of the cart-pole system" (2007). States x, x_dot, theta,
theta_dot; theta = 0 is upright. With cart mass M, pole mass m, pivot to
pole center of mass l, gravity g, and force F:

    theta_acc = ( g sin(th) + cos(th) (-F - m l thd^2 sin(th)) / (M + m) )
                / ( l (4/3 - m cos^2(th) / (M + m)) )
    x_acc     = ( F + m l (thd^2 sin(th) - theta_acc cos(th)) ) / (M + m)

Parameters, declared once in the flow block: M = 1 kg, m = 0.1 kg,
l = 0.5 m, g = 9.81 m/s^2, fall angle 0.6 rad.

## How the gains are derived

The full derivation is written out in `control.flow`. In short:

1. Linearize at the upright equilibrium. The Jacobian is analytic;
   `main.flow` reads the physical parameters back off the plant instance,
   so model and controller share one source of truth.
2. Discretize by forward Euler at the 10 ms control period, matching the
   integrator that `evolves as` compiles to.
3. Check controllability: the rank of [B, AB, A^2B, A^3B] is 4.
4. Iterate the discrete-time Riccati equation to its fixed point with
   Q = diag(1, 1, 10, 1) and R = 0.1. The input is scalar, so the matrix
   inverse in the textbook formula collapses to one division. P is
   symmetrized every sweep; the open loop is unstable, and an asymmetric
   rounding residue would otherwise grow through it and destroy
   convergence. Converges in 1160 sweeps to

       K = [-2.9651, -5.6052, -47.9456, -12.4333],   u = -K x

   which matches an independent numpy computation of the same iteration
   to four decimals.

## Run

    ./flow run apps/cartpole/main.flow
    ./flow gfx apps/cartpole/cartpole_gfx.flow

## What the self-checks assert

`main.flow` returns a distinct nonzero code for each failed check:

1. The linearized plant has controllability rank 4.
2. The Riccati iteration converged.
3. Open loop, released at 0.05 rad with zero force, the pole triggers the
   `when theta reaches` fall event within 3 s (it fires at 0.82 s).
4. No closed-loop state became NaN.
5. The controlled pole never reached the 0.6 rad fall cone.
6. Over the last 2 s of the 10 s run, |theta| stayed below 0.001 rad
   (measured: 5.7e-5 rad).
7. The cart ended within 0.05 m and 0.05 m/s of the track center.
8. The cart never strayed more than 1 m (measured peak: 0.53 m).

## Scope notes

- Integration is explicit Euler at 10 ms, the same scheme the gain was
  derived against. Peak force from the 0.25 rad start is 12 N; there is no
  actuator saturation in the model.
- Flow block members are f64 in this language version, so the model does
  not use `unit` types.
