# Music without a universal scale

An exploratory Flow engine for musical **gestures** rather than a catalog of Western notes. This is a small executable experiment, not an ethnomusicological model and not a claim that musical traditions reduce to microtonal pitch.

## Run

```bash
./flow run examples/music/representation_lab.flow
./flow audio examples/music/representation_audition.flow

# Render on a machine with no audio device
FLOW_AUDIO_RENDER=build/audio/representation_audition.wav \
  ./flow audio examples/music/representation_audition.flow
```

The lab returns nonzero on failure. It tests a held-out pair of synthetic gestures, two nearby pitch landmarks that collide under a 100-cent grid, loss of contours, onset and release interpolation, timing preservation, articulation preservation, and negative-cent rounding.

The audition plays eight seconds. Seconds 0-4 use a 100-cent fixed-grid, note-only baseline; seconds 4-8 use observation-derived pitch landmarks and retain the original trajectory and articulation. The example intentionally uses a fixed one-second presentation slot, so it **does not** audition its duration differences. It is not a measurement of cultural fidelity.

## Representation

The reusable core lives in `lib/stdlib/music/representation.flow`.

`MusicGesture` carries an onset pitch, a crest pitch at 40% of the gesture, a release pitch, duration in beats, and an opaque articulation code. All three pitch values are **cents relative to a caller-provided reference**. They are not MIDI numbers, note names, or degrees of any predefined musical scale. Reference frequency, tonic stability, and phrase function are not yet learned.

`music_discover_landmarks` starts with the first observed onset and repeatedly introduces the farthest observed onset from its existing pitch landmarks, stopping when the maximum training reconstruction error is within the specified bound or when the capacity is exhausted. It is deterministic farthest-first vector quantization, not a probabilistic learner. The fixed-capacity output means no allocation is needed to learn the landmarks. The caller must supply valid pointers and count/capacity matching their buffers.

`music_project_gesture` snaps the onset to a learned pitch landmark but retains crest and release **relative to that onset**, together with the original duration and articulation. It deliberately permits a learned pitch representation to coexist with an independent expressive contour representation.

`music_project_fixed_grid` is deliberately information-poor: round onset to the nearest multiple of 100 cents, set the entire trajectory to that onset, round beat duration to the nearest quarter, and discard articulation. This models one impoverished interchange format, **not Western music generally**, which has expressive performance practices too.

`music_measure_loss` returns disaggregated metrics. Onset error and contour error are in squared cents, duration error is in squared beats, and articulation loss is a mismatch count. These components have different units and **must not be summed** without an explicit loss policy. This makes representation loss inspectable rather than hiding it behind a single quality score.

## Research trajectory

The core also exposes `music_find_onset_collision`, which returns an explicit pair of distinct source onsets that collapse after the fixed-grid projection. This is a concrete, inspectable distinction-loss witness, rather than relying on a single aggregate error.

The first test answers a narrow question: can a representation learned from a phrase keep distinctions a fixed semitone grid removes? The example deliberately places two synthetic landmarks at 180 and 220 cents; both round to 200 cents in the baseline. The learned codebook preserves both. The held-out notes reuse observed onset locations with new gestures, so the result demonstrates **expressive transfer with known pitch landmarks**, not generalization to novel modes.

The next substantive research stage is **representation induction, not merely codebook growth**. Introduce phrase-conditioned, time-varying latent features and competing candidate model families: onset dictionaries; directional phrase-transition models; relative interval distributions; continuous contour families; rhythmic/contextual grammars; and articulations learned from recordings. Separate observed frequency ratios from asserted cultural or perceptual interpretations. Optimize predictive/interventional usefulness under a complexity budget, with an explicit unrepresented-information ledger.

For real tradition-based experiments, datasets must be documented with provenance, permission, performer context, phrase boundaries, tuning reference, uncertainty, and evaluations with practitioners. Do not label synthetic cent offsets as a raga or maqam. Benchmark against 12-TET MIDI export, high-resolution MIDI pitch bend, raw pitch-trajectory storage, and sequential probabilistic models: pitch distortion alone is not a fair benchmark.

A future cross-representation mapping should preserve distinction certificates: if two gestures or their future continuations are distinguishable in one representation but collapse in another, return the witnessed pair and the specific dimensions lost (pitch, trajectory, timing, articulation, context). Such certificates would be a stronger contribution than the current nearest-landmark engine.

## Scope and limitations

There is no automatic audio transcription, source separation, cultural style inference, learnable phrase grammar, multiple timbres, ontology search, or real-time plug-in integration in this first increment. Real-time synthesis in the audition uses Flow's existing oscillator and sink. The landmark learner runs outside the audio callback. The demonstration is a controlled information-loss experiment, not evidence of having learned a musical tradition.
