# arXiv preprint: Schur-Lattice Colligations for Many-Pole All-Pass Filters

**PDF:** `schur_lattice_allpass.pdf`, perturbation-theoretic framing (structured $\delta k$ vs unstructured $\Delta a$ on the Schur disk)

## Files

| File | Purpose |
|------|---------|
| `schur_lattice_allpass.tex` | arXiv LaTeX source |
| `../formal/SchurLatticeAllpass/` | Mathlib proofs |

## Build PDF

```bash
cd docs/research/schur_lattice_allpass
pdflatex schur_lattice_allpass.tex
```

## Verification plots

```bash
python3.12 tools/plot_lattice_allpass.py
open build/plots/schur_lattice_allpass/schur_lattice_novel_demo.png
```

| Figure | What it proves |
|--------|----------------|
| `schur_lattice_novel_demo.png` | **Hero figure**, pipeline, lattice vs naive coeff wobble, phase sculpting, 16-pole O(n), Givens colligation, 60 Hz per-sample k retune |
| `schur_lattice_allpass_overview.png` | Lean + Flow verification dashboard |
| `flow_python_magnitude_check.png` | Runtime matches reference (legacy) |
| `dsp_bode_pz_groupdelay.png` | Bode magnitude/phase, group delay, pole-zero |
| `dsp_impulse_step.png` | Impulse + step response |
| `audio_waveforms.png` | Real audio: input vs static vs modulated |
| `audio_rms_envelope.png` | RMS envelope preserved (all-pass energy) |
| `audio_spectrograms.png` | Spectral content under modulation |
| `audio_modulation_proof.png` | Cross-correlation lag + k₁(t) LFO |

Audio WAV outputs: `build/audio/lattice_allpass/` (`input.wav`, `output_static_allpass.wav`, `output_modulated_allpass.wav`)

```bash
python3.12 tools/lattice_allpass_audio_demo.py
afplay build/audio/lattice_allpass/output_modulated_allpass.wav
```

Figures are copied to `figures/` after running the plot script.

## arXiv deposit checklist

1. Upload `schur_lattice_allpass.tex` (+ generated PDF)
2. Category: **eess.SP** (Signal Processing) or **cs.SD** (Sound)
3. Ancillary: `formal/SchurLatticeAllpass/` Lean sources
4. Code: Flow implementation in `lib/stdlib/dynamics/schur_lattice.flow`, `lib/stdlib/audio/lattice_allpass.flow`