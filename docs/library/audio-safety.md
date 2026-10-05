# Audio safety

Running an unfamiliar audio program with headphones on should not be able to produce unbounded digital output. `lib/stdlib/audio/safety.flow` is the standard safety chain used by the repository's audio examples.

The default teaching chain guards NaN/infinity, removes DC, flushes denormals, applies a stereo-linked lookahead limiter, fades both ends, caps duration, and finishes with a counted hard clamp. Per-sample functions are `@rt_safe` and use preallocated state.

## Use the complete checked example

The canonical usage, including `SampleRate`, `SafetyChain`, frame input, sink handling, reporting, and teardown, is kept in complete source rather than repeated here with undeclared `left`/`right` samples:

```bash
FLOW_HOST=python ./flow run tests/stdlib/audio/test_safety.flow
```

The implementation is `lib/stdlib/audio/safety.flow`; offline rendered-file checks are in `lib/stdlib/audio/verify.flow`.

## Signal chain

The processing order is NaN/infinity guard → DC blocker → denormal flush → lookahead brickwall limiter → fade/watchdog → final hard clamp.

A bad sample mutes the chain for the rest of the run and increments the NaN counter. Denormals below the library threshold are flushed to zero. The limiter is stereo-linked so gain reduction does not move the stereo image. The hard-clamp counter is intended to remain zero; a hit is evidence that an earlier invariant failed.

## Feedback guard

`feedback_guard` refuses magnitude at or above one and soft-clamps values close to one. `rt60_to_feedback` and `feedback_to_rt60` expose the audible tail length rather than asking users to guess a feedback coefficient.

For concrete calls and their surrounding imported declarations, use the checked audio examples and `tests/stdlib/audio/test_safety.flow` rather than an isolated fragment.

## Measured limiter behavior

The repository test drives a 1 kHz +12 dBFS sine into the default -6 dBFS chain at 48 kHz.

| Measurement | Value |
| --- | --- |
| Peak in | +12.00 dBFS |
| True peak in | +12.00 dBFS |
| Peak out | -6.0009 dBFS |
| True peak out | -6.0009 dBFS |
| Worst overshoot | 0.000000 linear |
| Worst gain reduction | -18.09 dB |
| Lookahead / latency | 96 samples (2.0 ms) |
| Onset to 1 dB reduction | 15 samples (0.31 ms) |
| Release to within 0.1 dB | 673 ms |
| Hard clamp hits | 0 |

The limiter targets slightly below the nominal ceiling so final `f32` rounding cannot push a sample over the limit.

## Configuring the chain

`SafetyConfig` exposes ceiling, fades, release/hold behavior, and watchdog configuration. Prefer the constructor helpers such as `safety_config_default`, `safety_config_ceiling`, and `safety_config_fades`; `safety_new_with` creates a chain from that configuration. The watchdog remains capped at `SAFETY_MAX_SECONDS`.

The exact function signatures live in `lib/stdlib/audio/safety.flow`, where they cannot drift from the implementation.

## Meters

The chain exposes input/output sample peak, true peak, RMS, maximum gain reduction, clamp count, NaN count, and a combined `safety_ok` result. Offline tests should gate on `safety_ok` and then verify the rendered file as well.

## Offline render verification

`verify_run` checks a WAV's format, duration, ceiling, non-silence, finite samples, fades, and expected dominant partial. Render all repository audio examples with:

```bash
scripts/render_audio_examples.sh
```

The script does not open an audio device; examples are rendered twice and the outputs must be byte-identical.

## Boundaries of the guarantee

The library controls digital signal level, not hardware volume. It cannot protect gain inserted downstream, a wrongly selected output device, or listening fatigue from a sustained signal that remains under the peak ceiling.

See `lib/stdlib/audio/safety.flow`, `lib/stdlib/audio/verify.flow`, `tests/stdlib/audio/test_safety.flow`, [audio basics](../tutorials/audio-basics.md), and [RT safety](rt-safety.md).
