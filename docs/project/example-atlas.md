# The Example Atlas: 100 simulations, and the argument they make

> **Purpose.** Every example here exists to demonstrate one claim: that a
> system which *evolves through time* is better expressed in Flow than in the
> Python/MATLAB/C toolchain it replaces. Each one must be honest about that —
> a demo that is merely pretty proves nothing.

## The argument

Three properties of Flow do the work, and every example should exercise at
least one of them visibly:

**1. The dynamics are declared, not hand-integrated.** A `flow` block states
what a quantity *is* and how it changes; the integrator is generated:

```flow
flow Neuron {
    state v: f64 = -65.0
    state u: f64 = -13.0
    param a: f64 = 0.02

    v evolves as 0.04 * v * v + 5.0 * v + 140.0 - u + I
    u evolves as a * (0.2 * v - u)

    when v reaches 30.0 { v becomes -65.0; u becomes u + 8.0 }
}
```

The reset is a first-class hybrid event, not an `if` buried in a loop. The
same source lowers to C and to MLIR.

**2. The cost model is visible.** No hidden allocation, no interpreter, no
array-library dispatch. A 128×128 reaction-diffusion step is the loop you
wrote, compiled through clang at native speed, with module statics for the
grids and `span<T>` for the views. Where a Python reference needs NumPy to
be tolerable, Flow needs nothing.

**3. Effects and capabilities separate model from environment.** The same
simulation core runs headless, into a window, or into a GIF, by swapping a
handler rather than editing the model.

## Method: every example carries evidence

An example is not done when it runs. It is done when it carries:

| Evidence | Meaning |
|---|---|
| **Correctness** | A known-answer check, a conservation law, an analytic solution, or a reference implementation it matches |
| **Formation** | For visual sims: a decoded early-vs-late frame comparison proving structure emerged |
| **Cost** | A measured number on the machine that ran it (ns/step, steps/s, or wall time) |
| **Comparison** | Where a claim of "better" is made: the reference implementation, and what it costs there |

Examples that cannot carry these get marked honestly rather than shipped as
proof.

## Domains and the 100

Counts are targets. Shipped counts update as work lands.

### 1. Morphogenesis and pattern formation — 20 shipped

Reaction-diffusion (Gray-Scott, Turing spots and stripes, Belousov, Swift-
Hohenberg, Cahn-Hilliard, anisotropic diffusion), growth and aggregation
(DLA, Eden, space-colonization venation, two L-systems, ballistic coral),
cellular (cyclic CA, Life variants, hex snowflake, WFC growth), and
biological pattern (Physarum, cell sorting, somitogenesis).

**Status: complete.** `examples/morphogenesis/` · [gallery](../demos/morphogenesis.md)

### 2. Neuron and network simulation — 15 planned

| # | Example | Evidence it must carry |
|---|---|---|
| 1 | Hodgkin-Huxley single compartment | Spike shape and threshold vs published values |
| 2 | Izhikevich neuron zoo | All 20 firing regimes from one model, parameter-swept |
| 3 | Leaky integrate-and-fire | F-I curve matches the closed-form solution |
| 4 | FitzHugh-Nagumo phase plane | Nullclines and limit cycle drawn live |
| 5 | Morris-Lecar bifurcation | Hopf point located numerically, matches analysis |
| 6 | Cable equation on a dendrite | Attenuation matches the analytic length constant |
| 7 | Multi-compartment neuron | Backpropagating action potential |
| 8 | STDP at one synapse | Weight-change curve vs the canonical window |
| 9 | Balanced E/I network | Asynchronous irregular state; CV(ISI) near 1 |
| 10 | Ring attractor | Bump persists and tracks input |
| 11 | Hopfield associative memory | Capacity curve vs the 0.138N bound |
| 12 | Winner-take-all circuit | Selection latency vs input contrast |
| 13 | Central pattern generator | Stable phase-locked gait |
| 14 | Spiking retina to V1 | Orientation tuning emerges |
| 15 | Reservoir computing | Memory capacity measured |

### 3. Circuit simulation — 12 shipped

| # | Example | Evidence it carries |
|---|---|---|
| 1 | `rc_rl_rlc` | All three step responses against their closed forms, by a `flow` block and by both MNA companions; worst 3.7e-4 |
| 2 | `mna_dc` | Two ladders against hand arithmetic in the header; worst 8.7e-16, and the gmin leakage is the size gmin predicts |
| 3 | `lc_tank` | 1000 lossless cycles: trapezoidal drifts 1.0e-9, backward Euler decays at exactly (1+w^2)^-200 per cycle; adaptive dt holds 3.6e-11 |
| 4 | `diode_iv` | Newton vs Shockley to 1.7e-12 on two sweeps, and 59.526 mV/decade recovered from the simulated curve |
| 5 | `bjt_curves` | 255 Ebers-Moll operating points against bisection, worst 6.7e-13; active-region gain is betaF to 1.0e-10 |
| 6 | `opamp` | DC gain to 1.6e-8, rolloff and phase from a single-bin DFT to 5.0e-5, and gain x bandwidth = A0 fp measured at two gains |
| 7 | `oscillator_colpitts` | Starts itself from a 20 ns kick; 2.246281 MHz against 1/(2 pi sqrt(L Ceq)), error 2.0e-3 |
| 8 | `buck_converter` | Vout follows D Vin to 3.0e-8 over seven duty cycles; both ripple formulas within 1e-3; the diode version loses exactly (1-D) Vf |
| 9 | `logic_delays` | A ripple-carry adder from 20 one-line `flow` gates: 512/512 sums correct, critical path 799.9930 ps against the sum of its stages |
| 10 | `transmission_line` | Six loads from near short to near open, reflection within 2.1e-3 of (ZL-Z0)/(ZL+Z0) |
| 11 | `chua` | Largest Lyapunov exponent 0.4316 by two methods agreeing to 5.3e-6, at three step sizes; volume contracts at -3.8155 |
| 12 | `pll` | Phase error, relaxation rate and capture time against the separable integral, to 1e-11, 1.2e-4 and 2.9e-5; lock range K |
| — | `netlist_demo` | A SPICE-subset front end feeding the same solver: three decks, checked to 1.9e-6, 1.1e-14 and 1.7e-16 |

**Status: complete.** `examples/circuits/` · solver
[`lib/stdlib/circuit.flow`](../../lib/stdlib/circuit.flow) · netlist front end
[`lib/stdlib/spice.flow`](../../lib/stdlib/spice.flow)

These are measurement programs rather than pictures: each one gates its exit
code on the number it printed, so none of them is a windowed demo and none
carries a GIF. Where a picture earns its place it is drawn in ASCII to stdout,
as `chua` does with its attractor.

### 4. Diffusion, transport and fields — 12 planned

Heat (1D/2D/3D, anisotropic, with sources), advection-diffusion with
upwinding, Fick's laws with a moving boundary (Stefan problem), Darcy flow
in porous media, Navier-Stokes lid-driven cavity (Re-swept against reference
vortex positions), shallow-water equations, wave equation with absorbing
boundaries, Schrödinger evolution (norm conservation as the check),
Fokker-Planck, percolation with a measured critical threshold, level-set
front propagation, lattice Boltzmann.

### 5. Physics and mechanics — 12 planned

N-body with symplectic integration (energy drift as the check), double
pendulum (Lyapunov exponent), rigid-body chains, cloth and mass-spring,
soft-body FEM, granular packing, orbital mechanics with a Hohmann transfer,
gyroscopic precession, coupled oscillators and synchronization (Kuramoto),
elastic collisions with restitution, projectile with drag vs the analytic
vacuum case, inverted pendulum on a cart (already shipped as the cart-pole
flagship — extend it).

### 6. Chemistry and biology — 10 planned

Chemical kinetics with stiff systems (Robertson problem — a real integrator
stress test), Gillespie stochastic simulation, enzyme kinetics
(Michaelis-Menten fitted from simulated data), gene regulatory networks
(repressilator, toggle switch), predator-prey with a limit cycle, epidemic
models (SIR/SEIR with an R0 sweep), population genetics drift, protein
folding on a lattice, chemotaxis, ecosystem food webs.

### 7. Control and estimation — 10 planned

PID with tuning comparison, LQR (already used in cart-pole), Kalman and
extended Kalman filters (estimation error vs Cramér-Rao), particle filter,
model-predictive control, adaptive control, sliding-mode control, system
identification from data, observability and controllability analysis
(`sense on` already ships), robust control margins.

### 8. Signals, audio and imaging — 9 planned

FFT and spectrogram, digital filter design and response, resonant filters,
physical modelling synthesis (Karplus-Strong, waveguides), room acoustics
via ray tracing, image convolution and edge detection, tomographic
reconstruction, optical flow, wavelets.

## Cross-cutting requirements

- **Every domain gets one "same model, two languages" comparison**: the Flow
  version beside a Python/NumPy or C reference, with both correctness and
  timing reported. This is where the "better represented" claim is either
  earned or withdrawn.
- **Every visual example gets a recorded GIF** via `flow record <prog> --gif`.
- **Every example is strict-clean** and runs in tier2.
- **Domain READMEs** carry the table; the atlas links them.

## Progress

| Domain | Planned | Shipped |
|---|---:|---:|
| Morphogenesis | 20 | 20 |
| Neuron and networks | 15 | 0 |
| Circuits | 12 | 12 |
| Diffusion and fields | 12 | 0 |
| Physics and mechanics | 12 | 1 |
| Chemistry and biology | 10 | 0 |
| Control and estimation | 10 | 2 |
| Signals and imaging | 9 | 0 |
| **Total** | **100** | **35** |

Related: [VISION.md](../../VISION.md) · [dynamics DSL](../language/dynamics-dsl.md) ·
[morphogenesis gallery](../demos/morphogenesis.md)
