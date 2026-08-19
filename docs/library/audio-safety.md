# Audio safety

Running an unfamiliar audio program with headphones on should not be able to
hurt you. `lib/stdlib/audio/safety.flow` is the chain that makes that true.
Every audio example in this repository runs through it, and so should
anything you write while you are learning.

The short version: a brickwall limiter with lookahead holds the output at
-6 dBFS, both ends of the render are faded, nothing runs longer than 30
seconds, NaN mutes the output instead of reaching the speaker, and asking
for a feedback coefficient of 1.05 is refused rather than granted.

## The chain

One stereo frame at a time, in this order:

```
NaN / infinity guard  ->  DC blocker  ->  denormal flush
  ->  lookahead brickwall limiter  ->  fade in / fade out + watchdog
  ->  hard clamp (last resort, counted)
```

```text
import "stdlib/audio/safety.flow"

let rate: SampleRate = sample_rate_48000()
let mut chain: SafetyChain = safety_new(rate, 3.0)   # three seconds
let cp: ptr<SafetyChain> = &chain

while !safety_finished(cp) {
    let out: Frame = safety_process_frame(cp, left, right)
    # write out.left / out.right
}
safety_report(cp)
```

Everything on the per-sample path carries `@rt_safe`: no heap, no locks,
fixed bounds. The whole chain is one stack allocation, which is why it is
safe to call from an audio callback.

### NaN and infinity guard

`sample_is_bad` is true for NaN and for anything past plus or minus 1e30. A
bad sample mutes the chain for the rest of the run and increments
`safety_nan_count`. It does not try to recover: a DSP graph that has
produced one NaN will keep producing them, and a muted render that reports
the fault is more useful than an intermittent one.

### DC blocker

A one-pole highpass at about 10 Hz, per channel. DC costs headroom without
being audible and can push a speaker cone off centre. Its passband gain at
440 Hz is 1.00015, so it is not doing anything you can hear. It does have a
start-up transient of a few tens of milliseconds, which is one reason the
fade-in exists.

### Denormal flush

Anything below 1e-20 in magnitude is flushed to zero. Denormals cost
hundreds of cycles per operation on some CPUs and are inaudible either way.
This matters most in reverb and delay tails, which is exactly where a signal
spends a long time being very small.

### Lookahead brickwall limiter

Stereo-linked, so the image never shifts when it works. Per sample, with
lookahead `L`:

```
raw[n]  = min(1, ceiling / truepeak[n])     instantaneous requirement
env[n] <= raw[n]                            program-dependent release
held[n] = min(env[n-L+1 .. n])              running minimum
gain[n] = mean(held[n-L+1 .. n])            moving average, L long
out[n]  = in[n-L] * gain[n]
```

Every term in that average is the minimum of `env` over a window ending at
or before `n`, so every term is at most `raw[n-L+1]`, so the average is at
most `raw[n-L+1]`, which is the gain that holds the true peak covering input
sample `n-L` at the ceiling. The output sample is `in[n-L]`. That is the
whole proof, and it is why the hard clamp after the limiter should never
fire. `safety_clamp_count` is a bug counter, not a reading.

Peak detection is true peak, not sample peak: a Catmull-Rom spline through
four consecutive samples is probed at a quarter, a half and three quarters
of the interval. Catmull-Rom overshoots a band-limited reconstruction
slightly, so the reading errs high, which for a limiter is the safe
direction.

### Fades

`fade_gain(t) = sin(pi/2 * t)`, so `gain^2` rises like a quarter sine and
the perceived loudness ramp is even. `fade_gain(0)` is exactly zero, which
is what makes the first and last sample of every render silent. Default
length is 15 ms at each end.

### Duration watchdog

`safety_new(rate, seconds)` caps at `SAFETY_MAX_SECONDS`, which is 30. Ask
for 45 and you get 30, a printed warning, and `safety_watchdog_hit` returns
true. Past the end the chain returns silence rather than continuing, so a
stuck oscillator stops being a problem at a known time.

### Feedback guard

```text
feedback_guard(1.05)              # refused, returns 0.0, prints why
feedback_guard(0.995)             # clamped to 0.98, prints that it clamped
rt60_to_feedback(3.0, 0.375)      # 0.4217: a 3 second tail on a 375 ms delay
feedback_to_rt60(0.4217, 0.375)   # 3.00 seconds, back again
```

A magnitude at or above 1 is refused outright and becomes 0. There is no
sensible substitute for "make this louder forever". Between
`FEEDBACK_SOFT_MAX` (0.98) and 1 the value is clamped and the caller is
told, because the tail would outlast the watchdog.

Ask for a tail in seconds. `rt60_to_feedback` is the honest interface: you
know how long you want the echo to last, and you do not know what 0.87
sounds like on a 375 ms delay.

One thing the guard does not cover: `delay_line_set_feedback` in
`stdlib/audio/delay_line.flow` silently clamps anything at or above 1 to
0.99 without saying so. Route through `feedback_guard` first if you want to
be told.

## Measured limiter behaviour

A 1 kHz sine at **+12 dBFS** (four times full scale), stepped on at 0.5 s
and off at 2.0 s, into the default chain with its -6 dBFS ceiling. These
figures come from `tests/stdlib/audio/test_safety.flow` on an Apple silicon
Mac at 48 kHz; run it yourself and the numbers should match to the digit,
because nothing in the chain depends on the machine.

| Measurement | Value |
| --- | --- |
| Peak in | +12.00 dBFS |
| True peak in | +12.00 dBFS |
| Peak out | -6.0009 dBFS |
| True peak out | -6.0009 dBFS |
| Worst overshoot above the ceiling | 0.000000 (linear) |
| Worst gain reduction | -18.09 dB |
| Lookahead / added latency | 96 samples (2.0 ms) |
| Onset to 1 dB of reduction | 15 samples (0.31 ms) |
| Release to within 0.1 dB of unity | 673 ms |
| Hard clamp hits | 0 |

Read that as: 18 dB of gain reduction arrived inside the 2 ms of lookahead,
not one sample got out above the ceiling, and the hard clamp behind the
limiter never had to do anything. The 673 ms release is the slow end of the
program-dependent release, which is what you get after 18 dB of reduction;
a single transient recovers in tens of milliseconds instead.

The -6.0009 rather than -6.0000 is deliberate. The limiter aims at
`ceiling * 0.9999` so that f32 rounding in the final multiply cannot push a
sample one ULP over and trip the clamp. That is -0.00087 dB.

## Overriding the ceiling

-6 dBFS is a teaching default, chosen because tutorials get run by people
who have no idea how loud their system is set. Real work usually wants
something else.

```text
# -1 dBFS, which is where you would master to, keeping every other default.
let cfg: SafetyConfig = safety_config_ceiling(safety_config_default(), -1.0)
let mut chain: SafetyChain = safety_new_with(rate, 8.0, cfg)
```

`safety_config_fades(cfg, fade_in_ms, fade_out_ms)` does the same for the
fades. The `SafetyConfig` fields are all public if you want to set the
release times or the hold directly, but the watchdog is still capped at
`SAFETY_MAX_SECONDS` whatever you put in `max_seconds`.

Setting the ceiling to 0 dBFS is allowed. It is still a brickwall, so
nothing clips, but there is no longer any margin for whatever comes after
you in the chain.

## Reading the meters

`safety_report(cp)` prints the lot. Individually:

| Call | What it tells you |
| --- | --- |
| `safety_peak_in_db` / `safety_peak_out_db` | sample peak, before and after |
| `safety_true_peak_in_db` / `safety_true_peak_out_db` | inter-sample peak |
| `safety_rms_in_db` / `safety_rms_out_db` | RMS over the whole render |
| `safety_max_gain_reduction_db` | worst the limiter had to work |
| `safety_clamp_count` | should be 0; anything else is a limiter bug |
| `safety_nan_count` | should be 0; anything else is a DSP bug |
| `safety_ok` | all of the above, as one bool |

`safety_ok` is what an offline test should gate on. For a render written to
disk, `stdlib/audio/verify.flow` goes further and checks the file itself.

## Checking a render offline

`verify_run` reads a WAV back and asserts on the samples. This is how the
audio examples are covered on a machine with no sound card.

```text
if sink_is_render() {
    let spec: VerifySpec = verify_spec(6.0, safety_ceiling_db(cp), 110.0)
    if !verify_run(sink_render_path(), spec) {
        return 1
    }
}
```

It checks format, duration, peak against the ceiling, that the file is not
silent, that no sample is NaN or infinite, that both fades are present, and
that the loudest partial is the frequency you said you would play. That last
one is a Goertzel bank: bin 0 is the expected frequency, the rest is a
semitone ladder from 55 Hz to just under Nyquist, and the check passes only
if bin 0 wins. A tone one semitone off fails it.

Render every example and check all of them with:

```
scripts/render_audio_examples.sh
```

No device is opened. Each example is rendered twice and the two files must
be byte-identical.

## What this does not protect you from

- **Your system volume.** The chain controls the digital level. If the
  hardware volume is at maximum, -6 dBFS is still loud.
- **Anything downstream of the chain.** Gain applied after
  `safety_process_frame` is gain the limiter never saw.
- **A device that is not the one you think it is.** `sink_open` opens the
  default output. Check it before you put headphones on.
- **Sustained level.** The limiter bounds the peak. A -6 dBFS square wave
  for thirty seconds is inside every guarantee here and is still fatiguing.

## See also

- `lib/stdlib/audio/safety.flow`, the implementation
- `lib/stdlib/audio/verify.flow`, the offline checks
- `tests/stdlib/audio/test_safety.flow`, the audit that produced the table
- `docs/tutorials/audio-basics.md`, which uses the chain from lesson one
- `docs/library/rt-safety.md`, for what `@rt_safe` means
