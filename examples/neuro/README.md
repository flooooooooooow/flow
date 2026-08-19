# examples/neuro: spiking dynamics, and the numbers that prove it

Fifteen programs about how neurons and networks of neurons behave in time.
Every one of them measures the thing it is demonstrating, prints the
measurement beside the published value it should match, and returns a
nonzero exit code if it does not. They are regression tests that happen to
draw pictures. Recorded clips of all fifteen are in the
[neuron gallery](../../docs/demos/neuro.md).

This is the second domain of [the Example Atlas](../../docs/project/example-atlas.md),
after [`morphogenesis/`](../morphogenesis/README.md). It exists to make one
argument, the one in [VISION.md](../../VISION.md): a system that evolves
through time is better written as a statement of how it evolves than as a
loop that steps it. Neuroscience is a fair test of that, because the models
are famous, the reference numbers are published, and the equations are short
enough to fit in the header of a file.

## The dynamics are declared

Wherever the model is a differential equation, it is one. Hodgkin and
Huxley's four equations are four `evolves as` lines and nothing else:

```flow ignore="illustrative code skeleton"
flow HH {
    state v : f64 = -65.0
    state m : f64 = 0.05293
    state h : f64 = 0.59612
    state n : f64 = 0.31768

    param i_ext : f64 = 0.0
    ...
    solver { dt 10 us  method rk4 }

    v evolves as (i_ext
                  - gna * m * m * m * h * (v - ena)
                  - gk * n * n * n * n * (v - ek)
                  - gl * (v - el)) / cm
    m evolves as alpha_m(v) * (1.0 - m) - beta_m(v) * m
    h evolves as alpha_h(v) * (1.0 - h) - beta_h(v) * h
    n evolves as alpha_n(v) * (1.0 - n) - beta_n(v) * n
}
```

A spike reset is a hybrid event, not an `if` inside a loop:

```flow ignore="illustrative code skeleton"
when v reaches 30.0 {
    v becomes c
    u becomes u + d
}
```

and that one block is what turns the Izhikevich model into twenty different
neurons. Where a model is genuinely discrete - Hopfield's sign update, the
echo state map, the weight of an STDP synapse - there is no `flow` block and
the file says so rather than dressing a difference equation up as an ODE.

One more idiom worth naming: `balanced_network.flow` reuses a single
`LIFNeuron` value for all 12500 cells, the way the morphogenesis examples
reuse one cell for a whole grid. That is safe even with a `when ... reaches`
event, because the generated guard always ends a step below threshold, so
the next neuron starts from a clean guard.

## The fifteen

| Example | Model | What it proves | Measured | Reference |
|---|---|---|---|---|
| [`hodgkin_huxley.flow`](hodgkin_huxley.flow) | Hodgkin-Huxley, four gates | Spike shape and firing threshold | peak +40.26 mV, half-width 1.480 ms, onset 6.213 uA/cm2 | Hodgkin & Huxley 1952; onset 6.2 (Rinzel & Miller 1980) |
| [`izhikevich_zoo.flow`](izhikevich_zoo.flow) | Izhikevich quadratic model | Twenty firing regimes from one pair of equations | 20 of 20 panels satisfy their predicate | Izhikevich 2004, figure 1 |
| [`lif_fi_curve.flow`](lif_fi_curve.flow) | Leaky integrate-and-fire | F-I curve against the closed form | worst error 512 ppm over 24 currents | Gerstner et al. 2014, eq. 1.6 |
| [`fitzhugh_nagumo.flow`](fitzhugh_nagumo.flow) | FitzHugh-Nagumo | Nullclines, Hopf window, limit cycle | window [0.33128, 1.41872]; ringing 22.667 vs 22.661 | FitzHugh 1961; Nagumo 1962 |
| [`morris_lecar.flow`](morris_lecar.flow) | Morris-Lecar, type II | Hopf point located numerically | 93.8576 uA/cm2; fold at 88.300 | Morris & Lecar 1981; Rinzel & Ermentrout 1998 (93.86, 88.3) |
| [`cable_equation.flow`](cable_equation.flow) | Rall's passive cable | Attenuation vs the analytic length constant | worst error 0.17 % over six lambdas | Rall 1959; Dayan & Abbott eq. 6.30 |
| [`multicompartment.flow`](multicompartment.flow) | Active soma, passive dendrite | Backpropagating action potential | 296 us per compartment, tip at 10.7 % | Stuart & Sakmann 1994; Rall 1977 |
| [`stdp_window.flow`](stdp_window.flow) | Pair-based STDP | The canonical asymmetric window | worst deviation 1.05e-14 over 201 delays | Bi & Poo 1998; Song, Miller & Abbott 2000 |
| [`balanced_network.flow`](balanced_network.flow) | 12500 LIF neurons, sparse E/I | The asynchronous irregular state | rate 15.470 Hz vs 15.112 mean-field; CV 0.795 | Brunel 2000 |
| [`ring_attractor.flow`](ring_attractor.flow) | Cosine ring of rate units | A bump that remembers and tracks | drift 0.00000 deg/s; tracks 30 deg/s at 30.000 | Ben-Yishai et al. 1995; Zhang 1996 |
| [`hopfield.flow`](hopfield.flow) | Hopfield associative memory | Capacity against the 0.138 N bound | 0.166; 225280 updates, none raising the energy | Hopfield 1982; Amit, Gutfreund & Sompolinsky 1985 |
| [`wta_circuit.flow`](wta_circuit.flow) | Winner-take-all | Selection latency vs contrast | slope 9.068 ms vs 9.091 predicted, R^2 0.999991 | Amari & Arbib 1977; Douglas & Martin 2004 |
| [`cpg_gait.flow`](cpg_gait.flow) | Coupled phase oscillators | Four quadruped gaits, phase locked | worst phase error 0.000000 deg; recovery 0.12455 s vs 0.12500 | Collins & Stewart 1993; Golubitsky et al. 1999 |
| [`orientation_tuning.flow`](orientation_tuning.flow) | Retina to one V1 simple cell | Orientation tuning from untuned inputs | preferred 29.802 deg for a 30 deg axis; half-width 15.94 deg | Hubel & Wiesel 1962 |
| [`reservoir.flow`](reservoir.flow) | Echo state network | Memory capacity on the standard benchmark | MC 40.566 against the bound N = 100 | Jaeger 2001, 2002 |

## Running them

Every example draws itself, so they are built against the graphics backend.
The headless recorder is the one that gates: it runs the same compiled
program with no display, prints the evidence, and returns the program's exit
code.

```
# the regression run: prints the numbers, exits nonzero if any check fails
./flow record examples/neuro/hodgkin_huxley.flow --frames 90 \
    --out build/frames_hh --gif build/hodgkin_huxley.gif

# the same program in a window
./flow gfx examples/neuro/hodgkin_huxley.flow
```

`./flow run` does not link a graphics backend, so it cannot build these; use
`record` for the headless run and `gfx` for the window. The measurements are
all made before the window opens and do not depend on how many frames are
recorded, so `--frames 4` prints exactly the same numbers as `--frames 900`.

| Example | Record command |
|---|---|
| hodgkin_huxley | `./flow record examples/neuro/hodgkin_huxley.flow --frames 90 --out build/frames_hh --gif build/hodgkin_huxley.gif` |
| izhikevich_zoo | `./flow record examples/neuro/izhikevich_zoo.flow --frames 90 --out build/frames_izh --gif build/izhikevich_zoo.gif` |
| lif_fi_curve | `./flow record examples/neuro/lif_fi_curve.flow --frames 90 --out build/frames_lif --gif build/lif_fi_curve.gif` |
| fitzhugh_nagumo | `./flow record examples/neuro/fitzhugh_nagumo.flow --frames 90 --out build/frames_fhn --gif build/fitzhugh_nagumo.gif` |
| morris_lecar | `./flow record examples/neuro/morris_lecar.flow --frames 90 --out build/frames_ml --gif build/morris_lecar.gif` |
| cable_equation | `./flow record examples/neuro/cable_equation.flow --frames 90 --out build/frames_cable --gif build/cable_equation.gif` |
| multicompartment | `./flow record examples/neuro/multicompartment.flow --frames 90 --out build/frames_mc --gif build/multicompartment.gif` |
| stdp_window | `./flow record examples/neuro/stdp_window.flow --frames 90 --out build/frames_stdp --gif build/stdp_window.gif` |
| balanced_network | `./flow record examples/neuro/balanced_network.flow --frames 90 --out build/frames_bal --gif build/balanced_network.gif` |
| ring_attractor | `./flow record examples/neuro/ring_attractor.flow --frames 90 --out build/frames_ring --gif build/ring_attractor.gif` |
| hopfield | `./flow record examples/neuro/hopfield.flow --frames 90 --out build/frames_hop --gif build/hopfield.gif` |
| wta_circuit | `./flow record examples/neuro/wta_circuit.flow --frames 90 --out build/frames_wta --gif build/wta_circuit.gif` |
| cpg_gait | `./flow record examples/neuro/cpg_gait.flow --frames 90 --out build/frames_cpg --gif build/cpg_gait.gif` |
| orientation_tuning | `./flow record examples/neuro/orientation_tuning.flow --frames 90 --out build/frames_ori --gif build/orientation_tuning.gif` |
| reservoir | `./flow record examples/neuro/reservoir.flow --frames 90 --out build/frames_res --gif build/reservoir.gif` |

Or regenerate the whole gallery at once:

```
python3 scripts/record_demos.py --group neuro
```

The GIFs land in [`docs/demos/neuro/`](../../docs/demos/neuro.md).

## What "carries evidence" means here

Every file states, in its header, the model, the parameters, what it claims,
and the paper the claim comes from. Then it measures. Four kinds of check
appear, in rough order of how much they are worth:

**Against a closed form.** `lif_fi_curve` compares its simulated firing rate
with `1/(tau ln(RI/(RI - Vth)))`; `stdp_window` compares 201 measured weight
changes with `A exp(-|dt|/tau)`; `cable_equation` compares a fitted length
constant with `sqrt(Rm/Ri)` and with the exact discrete-chain answer. These
are known-answer tests for the compiler-generated integrator, and they hold
to parts in 1e12 or better where the mathematics allows it.

**Against the model's own linearisation.** `fitzhugh_nagumo` and
`morris_lecar` locate their Hopf points by bisection on `tr J = 0` and then
check the nonlinear simulation rings at `2 pi / sqrt(det J - (tr J)^2/4)`.
`wta_circuit` predicts its selection latency from the eigenvalue of the
competition, and `cpg_gait` predicts its recovery time from the graph
Laplacian. These catch the case where both the model and the measurement are
self-consistently wrong, because the two come from different directions.

**Against a published number.** Hodgkin and Huxley's spike peak and firing
threshold, Rinzel and Ermentrout's Hopf and fold currents, Bi and Poo's time
constants, Amit's 0.138, Jaeger's `MC <= N`.

**Against a conservation law or bound.** Hopfield's energy never increases
across 225280 asynchronous updates; the reservoir's capacity never exceeds
the number of units; the ring attractor's bump does not move when nothing
drives it.

## Where the models were adjusted, and why

Two files depart from their reference and say so in their header rather than
quietly.

`izhikevich_zoo` integrates twenty-five times more finely than Izhikevich's
own code, and applies the reset at the threshold crossing rather than after
a 0.25 ms Euler step has overshot it. Four of the twenty panels sit exactly
where that difference decides the outcome, so their numbers are adjusted:
panel A is run for 300 ms instead of 100 so the steady rate exists to be
measured, panel J's pulse drops from 2.0 to 0.4, panel Q's `d` from -21 to
-15, and panel T's from -2 to -0.5. The other sixteen are unchanged. The
cause is stated in the file: with a coarse step, `u` absorbs part of the
overshoot past the 30 mV cutoff, which effectively adds to `d`.

`balanced_network` uses Brunel's network size, connectivity and cell
parameters, but twice his synaptic weight and axonal delays spread over
0.5 to 3.0 ms rather than a single 1.5 ms. The larger weight puts sigma near
`theta - V_r`, which is what makes the firing fluctuation-driven; the spread
damps the delay-driven ripple a network of this size would otherwise carry.
Brunel's own synchrony measure still comes out at 0.050 rather than the
1e-4 of perfect independence, and the file says that too.

## Determinism

Every example seeds a deterministic generator and prints the same numbers on
every run. Where the pseudo-random stream matters - `balanced_network` draws
one Poisson sample per neuron per step from the same stream - it is
xorshift32 rather than a linear congruential generator, because an LCG's
serial correlation shows up in a network of 12500 neurons as population
events that are not there.
