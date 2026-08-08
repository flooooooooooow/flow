# Audio Examples

## rt_safe_callback.flow
Minimal `@rt_safe` process block — stack locals and fixed-bound loops only.
Compile-time checker rejects heap calls from `@rt_safe` (see `docs/library/rt-safety.md`).

```bash
./flow run examples/audio/rt_safe_callback.flow
```

## lattice_allpass_phase_engine.flow
Larger `@rt_safe` DSP demo (Schur lattice phase engine).

## loopback_effects.flow
Real-time input -> effect chain -> output loopback.

Requires the audio runtime backend configured (see `docs/library/audio.md`).

## offline_graph_demo.flow
Offline graph processing demo (no audio device required).

## bus_graph_demo.flow
Parallel bus routing demo (offline).

## gpu_gain_demo.flow
GPU gain demo (falls back to CPU if GPU unavailable).

## spectral_filter_design.flow
Showcase: designs four low-pass filters at 44.1 kHz with a 2000 Hz design
cutoff, each "perfect" in the textbook sense of its class:

- Hamming windowed-sinc FIR (33 taps, −6 dB point at fc)
- Spec-optimized Kaiser FIR (101 taps, β = 5.65 from the 60 dB stopband
  target, ≥ the Kaiser length formula for the 1600 Hz transition band)
- RBJ biquad with the exact Butterworth Q = 1/√2
- Bilinear one-pole with prewarped cutoff,
  c = (1 − tan(π·fc/fs))/(1 + tan(π·fc/fs)), whose half-power point
  (|H| = 1/√2, −3.0103 dB) lands exactly on fc — not the naive 1 − ωc
  Taylor approximation (−3 dB ~18% high) and not matched-z c = exp(−ωc)
  (−3 dB 0.45% high)

Every −3/−6 dB crossover is found by log-frequency bisection (exact to f32,
not grid-quantized), and the magnitudes at 4/8 kHz and DC are measured from
|H(f)|. The program renders an SVG magnitude-response + impulse-response
plot and a metrics table wrapped in a dark-themed HTML page to `build/` — all
from a single Flow program with no external plotting dependency.

```bash
FLOW_HOST=python ./flow run examples/audio/spectral_filter_design.flow
```

Full-language example (structs, sized arrays, string concat, FILE*/mkdir
externs, modified-Bessel via power series) — not Stage-A subset, native-only,
not in the wasm gallery.
