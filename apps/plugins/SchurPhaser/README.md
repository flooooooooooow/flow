# Schur Phase — JUCE VST3/AU

Many-pole spectral all-pass phaser using Schur-lattice cascade with per-sample reflection modulation.

## Features

- **Rate / Depth / Width / Mix** — core phaser controls
- **Stages / Tone / Spread** — spectral character
- VST3, AU, Standalone

## Build

```bash
cd apps/plugins/SchurPhaser
cmake -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --config Release
```

Plugins install to:
- macOS AU: `~/Library/Audio/Plug-Ins/Components/Schur Phase.component`
- macOS VST3: `~/Library/Audio/Plug-Ins/VST3/Schur Phase.vst3`
- Standalone: `build/SchurPhaser_artefacts/Release/Standalone/Schur Phase.app`

## DSP

Each section: \(H_i(z)=(k_i+z^{-1})/(1+k_i z^{-1})\). Design via Schur step-down on pole product; runtime modulates \(k_i\) with clip \(|k_i|<1\).

Matches `lib/stdlib/audio/lattice_allpass.flow` / `scripts/tools/lattice_allpass_audio_demo.py`.