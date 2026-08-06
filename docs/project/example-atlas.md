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

### 2. Neuron and network simulation — 15 shipped

| # | Example | Evidence it carries | Measured |
|---|---|---|---|
| 1 | Hodgkin-Huxley single compartment | Spike shape and threshold vs published values | peak +40.26 mV, half-width 1.480 ms, firing onset 6.213 uA/cm2 against 6.2 |
| 2 | Izhikevich neuron zoo | All 20 firing regimes from one model, parameter-swept | 20 of 20 panels satisfy a predicate drawn from the name of the regime |
| 3 | Leaky integrate-and-fire | F-I curve matches the closed-form solution | worst error 512 ppm over 24 currents |
| 4 | FitzHugh-Nagumo phase plane | Nullclines and limit cycle drawn live | Hopf window [0.33128, 1.41872]; ringing 22.667 vs 22.661 from the Jacobian |
| 5 | Morris-Lecar bifurcation | Hopf point located numerically, matches analysis | 93.8576 uA/cm2 against 93.86; fold of limit cycles 88.300 against 88.3 |
| 6 | Cable equation on a dendrite | Attenuation matches the analytic length constant | worst error 0.17 % over six length constants |
| 7 | Multi-compartment neuron | Backpropagating action potential | 296 us per compartment, distal tip at 10.7 % of the somatic peak |
| 8 | STDP at one synapse | Weight-change curve vs the canonical window | worst deviation 1.05e-14 over 201 delays |
| 9 | Balanced E/I network | Asynchronous irregular state; CV(ISI) near 1 | 15.470 Hz against 15.112 from the Siegert mean field; CV 0.795 |
| 10 | Ring attractor | Bump persists and tracks input | drift 0.00000 deg/s over ten seconds; tracks a 30 deg/s cue at 30.000 |
| 11 | Hopfield associative memory | Capacity curve vs the 0.138N bound | 0.166; energy never rose across 225280 updates |
| 12 | Winner-take-all circuit | Selection latency vs input contrast | slope 9.068 ms against 9.091 from the linearisation, R^2 0.999991 |
| 13 | Central pattern generator | Stable phase-locked gait | four gaits at 0.000000 deg phase error; recovery 0.12455 s against 0.12500 |
| 14 | Spiking retina to V1 | Orientation tuning emerges | preferred 29.802 deg for a 30 deg wiring axis, half-width 15.94 deg, OSI 1.0 |
| 15 | Reservoir computing | Memory capacity measured | MC 40.566 against Jaeger's bound of N = 100 |

**Status: complete.** `examples/neuro/` · [domain README](../../examples/neuro/README.md)

Each of the fifteen prints its measurements and returns a nonzero exit code
naming the first check that failed. Because they all draw, the gating run is
`./flow record <file> --frames 90 --out <dir> --gif <path>`, which builds
against the headless recorder and passes the program's exit status through.

### 3. Circuit simulation — 12 planned

| # | Example | Evidence |
|---|---|---|
| 1 | RC / RL / RLC transients | Match the analytic solution to tolerance |
| 2 | Modified nodal analysis solver | Reproduce a reference netlist's DC operating point |
| 3 | Transient analysis with adaptive dt | Energy conservation in an LC tank |
| 4 | Diode and BJT models | I-V curves vs Shockley / Ebers-Moll |
| 5 | Op-amp circuits | Gain and bandwidth vs theory |
| 6 | Colpitts / Wien oscillators | Oscillation frequency vs design equations |
| 7 | Switching converter (buck) | Ripple and duty-cycle relationship |
| 8 | Digital logic gate delays | Propagation through a ripple-carry adder |
| 9 | Transmission line | Reflection coefficients vs impedance mismatch |
| 10 | Chua's circuit | Double-scroll attractor, Lyapunov exponent |
| 11 | Phase-locked loop | Lock range and capture behaviour |
| 12 | Netlist front end | Parse SPICE-subset netlists into a `flow` block |

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
| Neuron and networks | 15 | 15 |
| Circuits | 12 | 0 |
| Diffusion and fields | 12 | 0 |
| Physics and mechanics | 12 | 1 |
| Chemistry and biology | 10 | 0 |
| Control and estimation | 10 | 2 |
| Signals and imaging | 9 | 0 |
| **Total** | **100** | **38** |

Related: [VISION.md](../../VISION.md) · [dynamics DSL](../language/dynamics-dsl.md) ·
[morphogenesis gallery](../demos/morphogenesis.md)
