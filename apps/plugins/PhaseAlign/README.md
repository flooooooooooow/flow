# Phase Align — JUCE VST3/AU

A corrective **phase rotator + time-alignment** tool. Reuses the Schur-lattice
all-pass engine from [`../SchurPhaser`](../SchurPhaser) — same filter, no
modulation — to rotate a track's phase without touching its magnitude, plus a
fractional delay line for sample-accurate alignment.

## Why all-pass?

An all-pass filter has **flat magnitude** and phase-only response, so it
re-times frequencies against each other with zero tonal coloration. Because the
lattice is parameterised by reflection coefficients `|k_i| < 1`, every setting is
**unconditionally stable**. Typical uses:

- Align a kick against a bass (or two mics on one source) — dial **Delay** for
  bulk timing, then rotate **Freq / Stages** to null the phase cancellation.
- Multi-mic drum phase (snare top/bottom, DI vs amp).
- Blend-friendly phase tricks with **Mix** for parallel processing.

## Controls

| Control  | Range        | Purpose                                              |
|----------|--------------|------------------------------------------------------|
| Delay    | 0–20 ms      | Fractional delay line for bulk time alignment        |
| Freq     | 20 Hz–20 kHz | Pivot frequency of the all-pass network              |
| Stages   | 1–8          | Rotation depth (each section ≈ 180° near the pivot)  |
| Spread   | 0–1          | Spreads sections ±1 octave for a broader rotation    |
| Invert   | on/off       | Polarity flip (180°)                                 |
| Mix      | 0–1          | Dry/wet blend (100% for pure correction)             |

The visualiser shows the **all-pass phase** against a 0° reference (or the
**group delay**), a marker at the pivot frequency, and the total corrective
latency `Δt` at the pivot.

## Build

```bash
cd apps/plugins/PhaseAlign
cmake -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --config Release
```

Installs to `~/Library/Audio/Plug-Ins/{VST3,Components}/Phase Align.*` and a
Standalone app under `build/PhaseAlign_artefacts/Release/Standalone/`.
