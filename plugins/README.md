# Flow Plugins — Schur Lattice in Native Audio

Two audio plugins for macOS, built with JUCE 8: **Schur Phase** and **Phase Align**. Both are native implementations of the many-pole Schur-lattice all-pass filter that the Flow project develops across the whole stack. This is the "juce rewrite" step: what began as research math and Flow code now runs in a DAW as real VST3/AU/Standalone plugins.

```
plugins/
├── SchurPhaser/            # many-pole spectral all-pass phaser (modulation)
│   ├── Source/
│   │   ├── SchurLatticeDSP.{h,cpp}   # shared DSP engine (also used by PhaseAlign)
│   │   ├── PluginProcessor.{h,cpp}   # APVTS, presets, audio-thread design
│   │   ├── PluginEditor.cpp          # controls + visualiser wiring
│   │   ├── PhaseScope.{h,cpp}        # 417-line spectrum/phase/scope UI
│   │   ├── PluginTopBar.h            # shared look-and-feel + bypass/AB bar
│   │   ├── SchurLookAndFeel.h        # custom paint (knobs, panel, graphs)
│   │   ├── SpectrumEngine.h          # FFT/magnitude analysis for the scope
│   │   ├── CorrelationMeter.h        # L/R correlation meter
│   │   └── AudioTap.h                # lock-free post-processing tap
│   └── tests/dsp_test.cpp            # correctness tests, no JUCE needed
└── PhaseAlign/             # corrective phase rotator + time alignment
    └── Source/
        ├── PluginProcessor.{h,cpp}   # all-pass + fractional delay, presets
        ├── PluginEditor.cpp          # tabbed editor with scope
        └── ScopeView.{h,cpp}         # phase/group-delay visualiser
```

## Where this filter lives in the project

The same lattice all-pass appears in four places, all derived from one design:

| Layer | Location | Form |
|-------|----------|------|
| Research | `docs/research/schur_lattice_allpass/` | arXiv paper, perturbation framing |
| Proof | `formal/SchurLatticeAllpass/` | Lean 4 proofs (Schur recursion, Givens, colligation) |
| Flow stdlib | `lib/stdlib/audio/lattice_allpass.flow`, `lib/stdlib/dynamics/schur_lattice.flow` | the language's own implementation |
| Reference | `tools/audio/lattice_allpass_audio_demo.py` | Python verification + WAV output |
| **Native** | `plugins/` (this tree) | JUCE VST3/AU/Standalone |

The plugin DSP is a port of the Flow stdlib design into C++. `SchurLatticeDSP.cpp` carries the math; the plugins add the DAW plumbing (parameters, presets, UI).

## The DSP

A cascade of first-order all-pass sections:

    H_i(z) = (k_i + z^-1) / (1 + k_i z^-1)

The coefficients `k_i` are reflection coefficients obtained by **Schur step-down** on a pole product. Because every `|k_i| < 1`, the network is unconditionally stable. The interesting part for a phaser is that `k_i` can be retuned **every sample** without touching the filter state, so the spectral sweep is click-free.

`SchurLatticeDSP.cpp` provides:

- `designFromPoles` / `schurStepDown` — pole product to reflections, O(n) per rebuild
- `processSample` — the cascade, per-sample modulation of `k_i`
- `fillModulatedK` — LFO wobble with per-section phase, stereo offset
- `computeResponse` — magnitude, wrapped phase, exact group delay, and the dry+wet comb (what the ear actually hears at a given mix) for the visualiser

The engine is deliberately free of JUCE dependencies. `tests/dsp_test.cpp` compiles against `SchurLatticeDSP.{h,cpp}` alone and checks the properties a production all-pass must hold:

1. magnitude flat to < 1e-3 dB across the band
2. analytic group delay matches the numeric derivative of the phase
3. every reflection coefficient satisfies `|k| < 1`
4. a single real pole maps to the expected first-order coefficient

```bash
cd plugins/SchurPhaser
./tests/run.sh        # builds with clang++ and runs all checks
```

## Schur Phase

Many-pole spectral phaser. Controls:

| Control | Range | Purpose |
|---------|-------|---------|
| Stages | 2–16 | Number of all-pass sections |
| Tone (color) | 0.2–0.9 | Pole radius, sets spectral character |
| Spread | 0–1 | Spreads the pole distribution |
| Rate | 0.05–12 Hz | LFO rate, or tempo-synced division |
| Depth | 0–0.35 | Modulation depth of the reflections |
| Width | 0–3.14 | Stereo phase offset between channels |
| Emphasis | −1..1 | Spectral tilt of the sweep |
| Mix | 0–1 | Dry/wet blend |

Eight factory presets (Init, Slow Sweep, Jet Flanger, Deep Notch, Sync 1/4, Sync 1/8T, Wide Shimmer, Subtle Warmth). The editor shows a live phase/spectrum scope fed by a lock-free post-process tap; the analyser curves are computed on the DSP thread and polled by the UI.

## Phase Align

A corrective phase rotator with time alignment, for fixing phase cancellation on multi-mic sources (kick vs bass, snare top/bottom, DI vs amp). Same lattice engine, no modulation: a fixed all-pass rotates phase while the fractional delay line handles bulk timing. Controls: Delay (0–20 ms), Freq (20 Hz–20 kHz pivot), Stages, Spread, Invert (polarity), Mix. The visualiser draws all-pass phase, group delay, the pivot marker, and the corrective latency.

## Build

**Schur Phase** builds from this tree. It needs CMake 3.22+, a C++17 toolchain, and the JUCE framework fetched via CMake's `FetchContent` (pinned to `8.0.6`). It also links the shared `TopBar` component from the Quilio SDK, which lives outside this repo:

```bash
cmake -S plugins/SchurPhaser -B build/schur -DCMAKE_BUILD_TYPE=Release -DQUILIO_SDK=/path/to/QuilioSDK
cmake --build build/schur --config Release
```

`QUILIO_SDK` defaults to `/Users/abhishekshivakumar/vstplugins/QuilioSDK`; point it at your own checkout.

**Phase Align** currently does not build from this repo on its own. Its `CMakeLists.txt` references shared UI sources (`quilio/UndoTree.cpp`, `quilio/ABSystem.cpp`, `quilio/PresetManager.cpp`, `quilio/TopBar.cpp`) under `SchurPhaser/Source/quilio/`, and that folder is not tracked here. Restore it from the Quilio SDK tree before building.

Install targets:

- AU: `~/Library/Audio/Plug-Ins/Components/`
- VST3: `~/Library/Audio/Plug-Ins/VST3/`
- Standalone app under `build/<name>_artefacts/Release/Standalone/`

## What's done so far

- Shared JUCE-independent DSP engine, ported from the Flow stdlib, with passing correctness tests
- Schur Phase builds as VST3, AU, and Standalone on macOS; Phase Align builds once its `quilio/` sources are restored
- Full APVTS parameter automation, factory presets, and state save/restore
- Audio-thread-safe design rebuilds (in-place coefficient updates, no state reset) and per-sample smoothing so parameter moves stay zipper-free
- Lock-free UI snapshot: the editor polls atomics to animate the scope without touching the audio thread
- Custom look-and-feel and scope/spectrum/correlation visualisers
- Lean proofs and the arXiv preprint covering the same filter, so the plugin math has a paper trail

## Known gaps

- Plugin builds are only validated on macOS; the Windows/Linux matrix is not wired up
- `PhaseAlign` depends on a `quilio/` shared-source folder under `SchurPhaser/Source/` that is not tracked in this repo, so it does not build from a fresh checkout
- The DSP correctness test runs in CI (`plugin-dsp` job) whenever `plugins/**` changes; full plugin builds are not yet in CI
