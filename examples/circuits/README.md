# examples/circuits: twelve circuits, each one gated on a measured number

Every program here prints what it measured, prints what the closed form says,
and exits non-zero if the two disagree. None of them is a picture of a
waveform. A circuit example that only draws a waveform proves that something
happened; these prove *what* happened, against arithmetic done independently
of the solver.

The domain is [the Example Atlas](../../docs/project/example-atlas.md)'s third
one. The claim being tested is the same as everywhere else in the atlas: that
a system evolving through time is better expressed in Flow than in the
toolchain it replaces. Circuits are a good place to test it because they are
the one domain where the answer is not always an ODE.

## Two representations, and the rule for choosing

A lumped circuit is a differential-algebraic system. Kirchhoff's current law
couples every node at once, and an ideal voltage source has no state at all,
so `v evolves as ...` cannot be written for a node whose voltage is pinned by
a source. Where that is the situation, these examples use
[`stdlib/circuit.flow`](../../lib/stdlib/circuit.flow), which builds the
modified-nodal-analysis matrix, factors it, and steps it. Where the circuit
really is an ODE once you have written it down properly, they use a `flow`
block with `evolves as` and the compiler generates the integrator.

Every file says which one it is and why, in its header. Four of the thirteen
programs are `flow` blocks:

```flow
flow LogicGate {
    state vout : f64 = 0.0
    param vtarget : f64 = 0.0
    param tau : f64 = 1e-10

    vout evolves as (vtarget - vout) / tau
}
```

Twenty copies of that line are the entire timing model of the ripple-carry
adder in `logic_delays.flow`, and the critical path it produces is the sum of
the individual gate delays to five decimal places.

## The programs

Run every command from the repository root.

| # | Example | Circuit | What it proves | Reference | Run |
|---|---|---|---|---|---|
| 1 | `rc_rl_rlc` | series RC, RL and RLC on a unit step | a `flow` block and both MNA companion models reproduce all three analytic step responses; worst normalized error **3.7e-4** | closed forms in the header: `V(1-e^-t/tau)`, `(V/R)(1-e^-t/tau)`, and the underdamped `1 - e^-at(cos + (a/wd) sin)` | `./flow run examples/circuits/rc_rl_rlc.flow` |
| 2 | `mna_dc` | a 3-rung 1 kohm ladder and a 14-node R-2R ladder | the DC operating point matches hand arithmetic to **8.7e-16**, and the default gmin's leakage is the size gmin predicts | fractions worked out in the header: 50/13, 20/13, 10/13 V, and exact halving from 8.192 V | `./flow run examples/circuits/mna_dc.flow` |
| 3 | `lc_tank` | lossless parallel LC, 1000 cycles | trapezoidal conserves energy to **1.0e-9** while backward Euler decays at exactly the rate its own pole predicts; the adaptive controller holds the same energy at **3.6e-11** | `(1+w^2)^-200` per cycle for backward Euler; energy constant for trapezoidal; f0 = 1/(2 pi sqrt(LC)) | `./flow run examples/circuits/lc_tank.flow` |
| 4 | `diode_iv` | diode alone, and a diode behind 1 kohm, swept -1 to 5 V | Newton reproduces Shockley to **1.7e-12**, and the simulated curve has the 59.526 mV/decade slope, recovered to **3.9e-9** | the Shockley equation, and 200 bisections on `Vd + R Is(exp(Vd/nVT) - 1) = V` | `./flow run examples/circuits/diode_iv.flow` |
| 5 | `bjt_curves` | Ebers-Moll NPN, 5 base currents x 51 collector voltages | the 3x3 Newton stamp reproduces Ebers-Moll everywhere to **6.7e-13**, and the active region has gain betaF to **1.0e-10** | bisection on the same equations in one scalar variable, which shares no arithmetic with the matrix solve | `./flow run examples/circuits/bjt_curves.flow` |
| 6 | `opamp` | one-pole macromodel, inverting and non-inverting, at two gains | DC gain to **1.6e-8** of `A0/(NG+A0)`, rolloff and phase to **5.0e-5** and **9.5e-4 deg**, and gain x bandwidth measured as **1000000.01 Hz** and **999999.97 Hz** at two different gains | `A_dc = NG A0/(NG+A0)`, `f_cl = fp (NG+A0)/NG`, and their product `A0 fp = 1 MHz` exactly | `./flow run examples/circuits/opamp.flow` |
| 7 | `oscillator_colpitts` | common-base Colpitts on an Ebers-Moll NPN | the circuit starts itself from a 20 ns kick and settles into a 1.58 V limit cycle at **2.246281 MHz**, an error of **2.0e-3** | `1/(2 pi sqrt(L Ceq))` = 2.250791 MHz with `Ceq = C1C2/(C1+C2)` | `./flow run examples/circuits/oscillator_colpitts.flow` |
| 8 | `buck_converter` | synchronous buck swept over duty, plus a diode version | Vout tracks D Vin with the conduction droop to **3.0e-8** across D = 0.2 to 0.8; ripple to **9.1e-4** and **1.9e-4**; the diode version loses exactly (1-D) Vf | `Vout = D Vin Rload/(Rload+Ron)`, `dIL = (Vin-Vout)D/(fsw L)`, `dV = dIL/(8 fsw C)`, and Shockley at the average inductor current | `./flow run examples/circuits/buck_converter.flow` |
| 9 | `logic_delays` | 4-bit ripple-carry adder from 20 `flow` gates | all 512 sums correct; the worst-case carry path measures **799.9930 ps** and every per-stage hop **170.0000 ps**; worst error **7.1e-5** | the sums written in the header: `4(tpd_AND + tpd_OR)` and `tpd_XOR + 4 tpd_AND + 4 tpd_OR`, with `tpd = tau ln 2` | `./flow run examples/circuits/logic_delays.flow` |
| 10 | `transmission_line` | 32 pi sections, six loads from near short to near open | the reflection read off the input node before and after the round trip is right to **2.1e-3** absolute; one-way delay **9.722 ns** | `Gamma = (ZL - Z0)/(ZL + Z0)` and `td = N sqrt(LC) = 10 ns` | `./flow run examples/circuits/transmission_line.flow` |
| 11 | `chua` | the double scroll as three `evolves as` lines | the largest Lyapunov exponent is positive at **0.4316** after Richardson extrapolation, from two methods agreeing to **5.3e-6**; volume contracts at **-3.8155** | the two exponents must agree, the two Richardson extrapolates must agree, and the average divergence must equal `f(1.2286) + (1-f)(-5.4571)` | `./flow run examples/circuits/chua.flow` |
| 12 | `pll` | phase-error model, first order and with a lag filter | steady phase error to **1.0e-11**, relaxation rate to **1.2e-4**, capture time to **2.9e-5**; lock range **6284.30 rad/s** against K; the filtered loop holds K and captures **0.626 K** | `arcsin(dw/K)`, `sqrt(K^2 - dw^2)`, the separable integral `(1/s) ln[u1(u2-U)/(u2(u1-U))]`, and the lock range K | `./flow run examples/circuits/pll.flow` |
| — | `netlist_demo` | three SPICE decks parsed off disk | the front end feeds the same solver: transient to **1.9e-6**, DC sweep to **1.1e-14**, operating point to **1.7e-16** | the analytic RLC step, bisection on Shockley, and 18/7 V and 12/7 V worked out in the deck's own comment header | `./flow run examples/circuits/netlist_demo.flow` |

## Cost, measured on the machine that ran them

Wall time for a complete run, clang -O2, Apple silicon:

| Example | Time | Example | Time |
|---|---:|---|---:|
| `mna_dc` | 0.01 s | `oscillator_colpitts` | 0.10 s |
| `rc_rl_rlc` | 0.03 s | `buck_converter` | 0.60 s |
| `lc_tank` | 0.10 s | `logic_delays` | 0.02 s |
| `diode_iv` | 0.01 s | `transmission_line` | 0.06 s |
| `bjt_curves` | 0.01 s | `chua` | 1.54 s |
| `opamp` | 0.03 s | `pll` | 0.73 s |
| `netlist_demo` | 0.01 s | **total** | **3.25 s** |

Some individual numbers behind those: `rc_rl_rlc` integrates 3.1 million steps
of three circuits by three methods; `lc_tank` takes 400 000 fixed steps and
576 000 adaptive ones; `buck_converter` runs 4.2 million switching steps across
seven duty cycles; `chua` takes 126 million Euler steps of a three-state
system with a tangent vector alongside.

## The solver

[`lib/stdlib/circuit.flow`](../../lib/stdlib/circuit.flow) is 1240 lines, a
good part of it the header and the comment on each stamp. It stamps R, C, L,
independent V and I, VCVS, VCCS, a Shockley diode and an Ebers-Moll NPN;
factors with dense LU and partial pivoting; steps with
backward Euler or the trapezoidal rule, fixed or with a step-doubling adaptive
controller; and solves nonlinear elements by Newton-Raphson with `pnjlim`
junction limiting and a reported iteration count.

The caps are consts backed by module statics and documented in the header: 80
non-ground nodes, 80 branch-current unknowns, matrix order 160, 256 elements.
The workspace is one 160x160 dense matrix, 205 kB, allocated once on first use.
Nothing allocates per step.

Two things worth pointing at:

**The factorization is reused when the matrix is provably unchanged.** The
buck converter takes 600 000 steps at one duty cycle and pays for 601 LU
factorizations, one per switching edge; every other step is a triangular
solve. The transmission line, which is linear with a fixed step, factors its
67x67 matrix once and then solves 4000 times.

**Initial conditions get a real t = 0.** The trapezoidal companion needs the
branch derivative at t = 0 as well as the state, and a bare initial condition
does not carry one. `circ_tran_init(true, dt_prime)` takes one microscopic
backward-Euler step to read the t = 0 currents, puts the state back exactly
where the caller asked for it, and rewinds the clock. Without that, the first
step of every trapezoidal run is wrong by O(dt) and the LC tank's energy
budget is off before it starts.

[`lib/stdlib/spice.flow`](../../lib/stdlib/spice.flow) is the netlist front
end. What it reads and what it does not are both listed by name in its header;
unsupported cards are counted, not silently dropped.

## Why there are no GIFs here

The atlas asks for a recorded GIF for every visual example. None of these is
visual: each one is a measurement that has to gate an exit code, and a
windowed program cannot do that. Where a picture genuinely helps, it is drawn
in ASCII to stdout and travels with the evidence: `chua` prints the x-y
projection of its attractor next to the exponent it measured from it.

Related: [the Example Atlas](../../docs/project/example-atlas.md) ·
[VISION.md](../../VISION.md) ·
[the dynamics DSL](../../docs/language/dynamics-dsl.md) ·
[examples/evolution](../evolution/README.md)
