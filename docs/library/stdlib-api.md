# Standard Library API (generated)

> Auto-generated from `lib/stdlib/` on 2026-08-06 by `scripts/gen_stdlib_docs.py`. Per-function docs come from `#` comments immediately above each `export function`.

**86** modules scanned.

## Modules

### `ai.flow`

Flow stdlib: game-AI trainers.  Three small trainer families for game agents, all storage in module statics

**Functions:**

| Name | Signature | Docs |
|------|-----------|------|
| `ai_seed` | `(seed: u32) -> void` | — |
| `ai_rand_range` | `(n: i32) -> i32` | Uniform integer in [0, n). n <= 0 returns 0. |
| `ai_rand_f32` | `() -> f32` | Uniform f32 in [0, 1). |
| `ai_rand_signed` | `() -> f32` | Uniform f32 in [-1, 1). |
| `ai_rand_gauss` | `() -> f32` | Approximately normal (sum of three uniforms, rescaled to std ~1). |
| `ai_hash_mix` | `(x: i32) -> i32` | 32-bit integer mixing hash (fmix-style). Always returns a non-negative i32. Use it to fold game-state features into a Q-table state id. |
| `q_init` | `(seed: u32) -> void` | Zero the table and seed the shared RNG. |
| `q_value` | `(state: i32, action: i32) -> f32` | — |
| `q_best` | `(state: i32, n_actions: i32) -> i32` | Greedy action (ties break toward the lowest index). |
| `q_select` | `(state: i32, n_actions: i32, epsilon: f32) -> i32` | Epsilon-greedy action selection. |
| `q_update` | `(s: i32, a: i32, r: f32, s_next: i32, n_actions: i32, alpha: f32, gamma: f32) -> void` | One Q-learning update: Q(s,a) += alpha * (r + gamma * max_a' Q(s',a') - Q(s,a)) |
| `q_update_terminal` | `(s: i32, a: i32, r: f32, alpha: f32) -> void` | Terminal update: the target is just the reward (no bootstrap). |
| `q_epsilon` | `(step: i32, total: i32, eps_start: f32, eps_end: f32) -> f32` | Linear epsilon decay: eps_start at step 0, eps_end at step >= total. |
| `ga_init` | `(pop: i32, dim: i32, seed: u32) -> void` | Random population of `pop` genomes with `dim` genes each, in [-1, 1). |
| `ga_pop_size` | `() -> i32` | — |
| `ga_genome_dim` | `() -> i32` | — |
| `ga_get` | `(i: i32, j: i32) -> f32` | — |
| `ga_set` | `(i: i32, j: i32, v: f32) -> void` | — |
| `ga_fitness_set` | `(i: i32, f: f32) -> void` | — |
| `ga_best_index` | `() -> i32` | — |
| `ga_best_fitness` | `() -> f32` | — |
| `ga_evolve` | `(elite_frac: f32, mutate_sigma: f32) -> void` | One generation: keep the top elite_frac unchanged, refill the rest with tournament-selected parents, uniform crossover and gaussian mutation. Fitness values are reset to 0 afterwards; re-evaluate before the next evolve. |
| `mlp_init` | `(n_in: i32, n_hid: i32, n_out: i32, seed: u32) -> void` | Configure sizes (clamped to the static budget) and randomize weights. |
| `mlp_forward` | `(x: ptr<f32>) -> void` | Forward pass: caches input, hidden tanh activations and output logits. |
| `mlp_output` | `(j: i32) -> f32` | Output logit j from the last forward pass. |
| `mlp_argmax` | `() -> i32` | Greedy action from the last forward pass. |
| `mlp_prob` | `(j: i32) -> f32` | Softmax probability of action j (valid after mlp_sample or mlp_reinforce). |
| `mlp_sample` | `() -> i32` | Sample an action from the softmax over the last forward pass's logits. |
| `mlp_reinforce` | `(x: ptr<f32>, action: i32, advantage: f32, lr: f32) -> void` | REINFORCE step: one gradient-ascent update on advantage * log pi(action \| x). Runs its own forward pass, so it can replay stored (x, action) pairs. |
| `mlp_train_mse` | `(x: ptr<f32>, target: ptr<f32>, lr: f32) -> f32` | Supervised step: squared-error loss on the linear outputs, SGD update. Returns the loss before the update. |

### `array.flow`

Sum the first `size` elements of an f32 array.

**Functions:**

| Name | Signature | Docs |
|------|-----------|------|
| `sum` | `(arr: array<f32>, size: i32) -> f32` | Sum the first `size` elements of an f32 array. |

### `async.flow`

Async primitives via algebraic effects  Call sites perform `Async` / `AsyncIO` operations; a capability supplies the

**Effects:** `Async`, `AsyncIO`, `TcpEffect`, `Cont`

**Capabilities:** `BlockingTcp`, `SimulatedAsync`, `ThreadedAsync`, `FiberAsync`, `BlockingAsyncIO`, `NetpollAsyncIO`, `FiberCont`

**Functions:**

| Name | Signature | Docs |
|------|-----------|------|
| `tcp_listen` | `(port: i32) -> i32` | Convenience (not effect ops): listen/accept/close for echo demos. |
| `tcp_accept` | `(listen_fd: i32) -> i32` | — |
| `tcp_close` | `(fd: i32) -> i32` | — |
| `async_set_maxprocs` | `(n: i32) -> void` | — |
| `async_maxprocs` | `() -> i32` | — |
| `cont_scaffold_available` | `() -> i32` | — |
| `cont_demo_shift` | `() -> i32` | — |
| `cont_demo_reset` | `() -> i32` | — |
| `cont_arm_resume` | `(value: i32) -> void` | — |
| `cont_resume` | `(value: i32) -> i32` | — |
| `cont_has_pending` | `() -> i32` | — |
| `async_delay` | `(ms: i32) -> void` | Thin helpers (same ops; clearer call sites) |
| `async_spawn` | `(task_id: i32) -> void` | — |
| `async_join` | `(task_id: i32) -> i32` | — |
| `async_sleep_ms` | `(ms: i32) -> void` | — |
| `async_poll_read` | `(fd: i32, timeout_ms: i32) -> i32` | — |

### `audio/clock.flow`

Audio Clock Module - BPM, Tempo, and Timing  Makes rhythm and timing incredibly easy with BPM-based scheduling.

**Structs:** `Clock`, `TimeSignature`, `SwingClock`

**Functions:**

| Name | Signature | Docs |
|------|-----------|------|
| `clock_new` | `(bpm: f64, rate: SampleRate) -> Clock` | Create a clock at given BPM and sample rate |
| `clock_new_with_sig` | `(bpm: f64, rate: SampleRate, sig: TimeSignature) -> Clock` | Create a clock with custom time signature |
| `clock_slow` | `(rate: SampleRate) -> Clock` | Common BPM presets |
| `clock_medium` | `(rate: SampleRate) -> Clock` | — |
| `clock_fast` | `(rate: SampleRate) -> Clock` | — |
| `clock_house` | `(rate: SampleRate) -> Clock` | — |
| `clock_dnb` | `(rate: SampleRate) -> Clock` | — |
| `clock_techno` | `(rate: SampleRate) -> Clock` | — |
| `time_sig_4_4` | `() -> TimeSignature` | Time Signature Presets |
| `time_sig_3_4` | `() -> TimeSignature` | — |
| `time_sig_6_8` | `() -> TimeSignature` | — |
| `time_sig_5_4` | `() -> TimeSignature` | — |
| `time_sig_7_8` | `() -> TimeSignature` | — |
| `samples_per_beat` | `(clock: Clock) -> i64` | Get samples per beat |
| `samples_per_bar` | `(clock: Clock) -> i64` | Get samples per bar |
| `samples_per_measure` | `(clock: Clock) -> i64` | Get samples per measure (alias for bar) |
| `samples_per_whole` | `(clock: Clock) -> i64` | Get samples per whole note (4 beats in 4/4) |
| `samples_per_half` | `(clock: Clock) -> i64` | Get samples per half note (2 beats) |
| `samples_per_quarter` | `(clock: Clock) -> i64` | Get samples per quarter note (1 beat in 4/4) |
| `samples_per_eighth` | `(clock: Clock) -> i64` | Get samples per eighth note (half beat) |
| `samples_per_sixteenth` | `(clock: Clock) -> i64` | Get samples per sixteenth note |
| `samples_per_thirtysecond` | `(clock: Clock) -> i64` | Get samples per thirty-second note |
| `samples_per_quarter_dotted` | `(clock: Clock) -> i64` | Get samples per dotted quarter (1.5 beats) |
| `samples_per_quarter_triplet` | `(clock: Clock) -> i64` | Get samples per triplet quarter (2/3 beat) |
| `clock_on_beat` | `(clock: Clock, sample_pos: i64) -> bool` | Check if we're on a beat boundary (within tolerance) |
| `clock_on_bar` | `(clock: Clock, sample_pos: i64) -> bool` | Check if we're on a bar boundary |
| `clock_on_sixteenth` | `(clock: Clock, sample_pos: i64) -> bool` | Check if we're on a sixteenth note |
| `clock_current_beat` | `(clock: Clock, sample_pos: i64) -> i64` | Get current beat number (0-indexed) |
| `clock_current_bar` | `(clock: Clock, sample_pos: i64) -> i64` | Get current bar number (0-indexed) |
| `clock_beat_in_bar` | `(clock: Clock, sample_pos: i64) -> i32` | Get beat within current bar (0-3 for 4/4) |
| `clock_sixteenth_in_beat` | `(clock: Clock, sample_pos: i64) -> i32` | Get sixteenth note number within current beat (0-3) |
| `clock_set_bpm` | `(clock: Clock, new_bpm: f64) -> Clock` | Change BPM (returns new clock) |
| `clock_scale_tempo` | `(clock: Clock, factor: f64) -> Clock` | Multiply BPM by factor (for tempo changes) |
| `clock_double_tempo` | `(clock: Clock) -> Clock` | Double tempo (half-time -> normal) |
| `clock_half_tempo` | `(clock: Clock) -> Clock` | Half tempo (normal -> half-time) |
| `swing_clock_new` | `(bpm: f64, rate: SampleRate, swing: f64) -> SwingClock` | — |
| `swing_position` | `(sclock: SwingClock, sixteenth: i32) -> f64` | Get swung position for a sixteenth note (0-3 within beat) Even sixteenths (0, 2) play early, odd (1, 3) play late |
| `bpm_to_hz` | `(bpm: f64) -> f64` | Convert BPM to Hz (frequency of quarter notes) |
| `hz_to_bpm` | `(hz: f64) -> f64` | Convert Hz to BPM |
| `ms_per_beat` | `(clock: Clock) -> f64` | Get milliseconds per beat |
| `beats_per_second` | `(clock: Clock) -> f64` | Get beats per second |
| `delay_time_samples` | `(clock: Clock, note_value: f64) -> i64` | Calculate delay time in samples for a note value note_value: 1.0 = whole, 0.5 = half, 0.25 = quarter, etc. |
| `dotted` | `(note_value: f64) -> f64` | Dotted note value (multiply by 1.5) |
| `triplet` | `(note_value: f64) -> f64` | Triplet note value (multiply by 2/3) |

### `audio/control.flow`

Audio Control Utilities  Control-rate smoothing and parameter utilities.

**Structs:** `ParamSmoother`

**Functions:**

| Name | Signature | Docs |
|------|-----------|------|
| `param_smoother_new` | `(initial: f32, time_ms: f32, rate: SampleRate) -> ParamSmoother` | — |
| `param_smoother_set_target` | `(p: ParamSmoother, target: f32) -> ParamSmoother` | — |
| `param_smoother_tick` | `(p: ParamSmoother) -> ParamSmoother` | — |
| `param_smoother_value` | `(p: ParamSmoother) -> f32` | — |

### `audio/delay.flow`

Audio Delay Module  Delay lines and time-based effects.

**Structs:** `DelayState`, `PingPongState`, `AllpassDelay`, `CombFilter`, `ModDelay`

**Functions:**

| Name | Signature | Docs |
|------|-----------|------|
| `delay_new` | `(max_time: Seconds, rate: SampleRate) -> DelayState` | Create a delay with given time |
| `delay_set_time` | `(d: DelayState, time: Seconds, rate: SampleRate) -> DelayState` | Set delay time |
| `delay_set_feedback` | `(d: DelayState, fb: f32) -> DelayState` | Set feedback amount |
| `delay_set_mix` | `(d: DelayState, mix: f32) -> DelayState` | Set wet/dry mix |
| `delay_advance` | `(d: DelayState) -> DelayState` | Advance write position (call after writing sample) |
| `delay_read_pos` | `(d: DelayState) -> i64` | Calculate read position |
| `pingpong_new` | `(time: Seconds, rate: SampleRate) -> PingPongState` | Create ping-pong delay |
| `pingpong_set_feedback` | `(pp: PingPongState, fb: f32) -> PingPongState` | Set cross-feedback |
| `lerp` | `(a: f32, b: f32, t: f32) -> f32` | Linear interpolation between two samples |
| `cubic_interp` | `(y0: f32, y1: f32, y2: f32, y3: f32, t: f32) -> f32` | Cubic interpolation (Hermite) for smoother modulated delays |
| `allpass_delay_new` | `(time_ms: f32, coeff: f32, rate: SampleRate) -> AllpassDelay` | Create allpass delay |
| `allpass_delay_advance` | `(a: AllpassDelay) -> AllpassDelay` | Advance position |
| `comb_new` | `(time_ms: f32, feedback: f32, damping: f32, rate: SampleRate) -> CombFilter` | Create comb filter |
| `comb_advance` | `(c: CombFilter) -> CombFilter` | Advance position |
| `mod_delay_new` | `(base_time: Seconds, mod_depth_ms: f32, mod_rate: f32, rate: SampleRate) -> ModDelay` | Create modulated delay (chorus-like) |
| `mod_delay_tick` | `(m: ModDelay) -> ModDelay` | Advance modulation phase |
| `mod_delay_current_samples` | `(m: ModDelay) -> f32` | Get current delay time in samples (modulated) |
| `mod_delay_set_rate` | `(m: ModDelay, rate_hz: f32, sample_rate: SampleRate) -> ModDelay` | Set modulation rate |
| `mod_delay_set_depth` | `(m: ModDelay, depth_ms: f32, rate: SampleRate) -> ModDelay` | Set modulation depth |

### `audio/delay_line.flow`

Delay Line (F32) with Real Buffer Storage  Uses AudioBufferF32 for a real ring buffer implementation.

**Structs:** `DelayLineF32`

**Functions:**

| Name | Signature | Docs |
|------|-----------|------|
| `delay_line_empty` | `() -> DelayLineF32` | — |
| `delay_line_new` | `(max_ms: f32, rate: SampleRate) -> DelayLineF32` | — |
| `delay_line_set_time` | `(d: DelayLineF32, time_ms: f32, rate: SampleRate) -> DelayLineF32` | — |
| `delay_line_set_feedback` | `(d: DelayLineF32, fb: f32) -> DelayLineF32` | — |
| `delay_line_set_mix` | `(d: DelayLineF32, mix: f32) -> DelayLineF32` | — |
| `delay_line_tick` | `(d: DelayLineF32, input: f32) -> DelayLineF32` | — |
| `delay_line_output` | `(d: DelayLineF32) -> f32` | — |
| `delay_line_reset` | `(d: DelayLineF32) -> DelayLineF32` | — |

### `audio/effects.flow`

Audio Effects Module - Common Effects Processors  Ready-to-use effects: reverb, delay, distortion, chorus, etc.

**Structs:** `Delay`, `Distortion`, `Chorus`, `Compressor`, `Bitcrusher`, `Reverb`

**Functions:**

| Name | Signature | Docs |
|------|-----------|------|
| `delay_new` | `(time_samples: i32, feedback: f32, mix: f32) -> Delay` | Create a delay with time in samples (assumes 44.1kHz; use delay_new_at_rate for other sample rates) |
| `delay_new_at_rate` | `(time_samples: i32, feedback: f32, mix: f32, rate: SampleRate) -> Delay` | Create a delay with time in samples at a specific sample rate |
| `delay_quarter_note` | `(clock: Clock) -> Delay` | Create a delay synced to clock (quarter note) |
| `delay_eighth_note` | `(clock: Clock) -> Delay` | Create a delay synced to clock (eighth note) |
| `delay_dotted_eighth` | `(clock: Clock) -> Delay` | Create a delay synced to clock (dotted eighth - classic dub delay) |
| `delay_process` | `(delay: Delay, input: f32) -> f32` | Process one sample through delay Note: this returns only the output sample (matching the historical API); use delay_tick if you need the updated Delay state for the next call. |
| `delay_tick` | `(delay: Delay, input: f32) -> Delay` | Process one sample through delay, returning the updated Delay state (threading this back in on the next call gives a real running delay line). |
| `delay_output` | `(delay: Delay) -> f32` | Get the last output sample from a Delay (after delay_tick) |
| `distortion_new` | `(drive: f32, tone: f32, mix: f32) -> Distortion` | — |
| `distortion_light` | `() -> Distortion` | Presets |
| `distortion_medium` | `() -> Distortion` | — |
| `distortion_heavy` | `() -> Distortion` | — |
| `distortion_fuzz` | `() -> Distortion` | — |
| `distortion_process` | `(dist: Distortion, input: f32) -> f32` | Process one sample |
| `chorus_new` | `(rate: f32, depth: f32, mix: f32) -> Chorus` | — |
| `chorus_subtle` | `() -> Chorus` | Presets |
| `chorus_medium` | `() -> Chorus` | — |
| `chorus_wide` | `() -> Chorus` | — |
| `chorus_process` | `(chorus: Chorus, input: f32) -> f32` | Process one sample (simplified - would need LFO from oscillators) Note: this returns only the output sample (matching the historical API); use chorus_tick if you need the updated Chorus state for the next call. |
| `chorus_tick` | `(chorus: Chorus, input: f32) -> Chorus` | Process one sample through the chorus, returning the updated Chorus state |
| `compressor_new` | `(threshold: f32, ratio: f32, attack: f32, release: f32) -> Compressor` | — |
| `compressor_gentle` | `() -> Compressor` | Presets |
| `compressor_medium` | `() -> Compressor` | — |
| `compressor_hard` | `() -> Compressor` | — |
| `limiter` | `() -> Compressor` | — |
| `compressor_process` | `(comp: Compressor, input: f32) -> f32` | Process one sample (simplified envelope follower) |
| `bitcrusher_new` | `(bits: i32, sample_rate_div: i32) -> Bitcrusher` | — |
| `bitcrusher_lofi` | `() -> Bitcrusher` | Presets |
| `bitcrusher_telephone` | `() -> Bitcrusher` | — |
| `bitcrusher_crushed` | `() -> Bitcrusher` | — |
| `bitcrusher_process` | `(crusher: Bitcrusher, input: f32) -> f32` | Process one sample |
| `reverb_new` | `(room_size: f32, damping: f32, mix: f32) -> Reverb` | — |
| `reverb_small_room` | `() -> Reverb` | Presets |
| `reverb_medium_hall` | `() -> Reverb` | — |
| `reverb_large_hall` | `() -> Reverb` | — |
| `reverb_plate` | `() -> Reverb` | — |
| `reverb_process` | `(rev: Reverb, input: f32) -> f32` | Process one sample (simplified - full reverb needs comb filters) |

### `audio/envelopes.flow`

Audio Envelopes Module  Envelope generators for amplitude, filter, and modulation control.

**Structs:** `EnvStage`, `ADSR`, `AR`, `Ramp`, `ExpDecay`

**Functions:**

| Name | Signature | Docs |
|------|-----------|------|
| `stage_idle` | `() -> EnvStage` | — |
| `stage_attack` | `() -> EnvStage` | — |
| `stage_decay` | `() -> EnvStage` | — |
| `stage_sustain` | `() -> EnvStage` | — |
| `stage_release` | `() -> EnvStage` | — |
| `adsr_new` | `(attack: Seconds, decay: Seconds, sustain: f32, release: Seconds, rate: SampleRate) -> ADSR` | Create ADSR from time values |
| `adsr_new_ms` | `(attack_ms: f32, decay_ms: f32, sustain: f32, release_ms: f32, rate: SampleRate) -> ADSR` | Create ADSR with millisecond times (convenience) |
| `adsr_gate_on` | `(e: ADSR) -> ADSR` | Trigger envelope (gate on) |
| `adsr_gate_off` | `(e: ADSR) -> ADSR` | Release envelope (gate off) |
| `adsr_tick` | `(e: ADSR) -> ADSR` | Advance envelope by one sample |
| `adsr_value` | `(e: ADSR) -> f32` | Get current envelope value |
| `adsr_is_active` | `(e: ADSR) -> bool` | Check if envelope is active (not idle) |
| `adsr_is_idle` | `(e: ADSR) -> bool` | Check if envelope has finished |
| `adsr_reset` | `(e: ADSR) -> ADSR` | Reset envelope to idle state |
| `ar_new` | `(attack: Seconds, release: Seconds, rate: SampleRate) -> AR` | Create AR envelope |
| `ar_trigger` | `(e: AR) -> AR` | Trigger the envelope |
| `ar_tick` | `(e: AR) -> AR` | Advance by one sample |
| `ar_value` | `(e: AR) -> f32` | Get current value |
| `ar_is_active` | `(e: AR) -> bool` | Check if active |
| `ramp_new` | `(start_val: f32, end_val: f32, duration: Seconds, rate: SampleRate) -> Ramp` | Create a ramp |
| `ramp_start` | `(r: Ramp) -> Ramp` | Start the ramp |
| `ramp_set_target` | `(r: Ramp, target: f32, duration: Seconds, rate: SampleRate) -> Ramp` | Set new target (for smooth parameter changes) |
| `ramp_tick` | `(r: Ramp) -> Ramp` | Advance by one sample |
| `ramp_value` | `(r: Ramp) -> f32` | Get current value |
| `exp_decay_new` | `(time_constant_ms: f32, rate: SampleRate) -> ExpDecay` | Create exponential decay from time constant |
| `exp_decay_trigger` | `(e: ExpDecay) -> ExpDecay` | Trigger decay (start from 1.0) |
| `exp_decay_tick` | `(e: ExpDecay) -> ExpDecay` | Advance by one sample |
| `exp_decay_value` | `(e: ExpDecay) -> f32` | Get current value |

### `audio/filters.flow`

Audio Filters Module  Digital filters for audio processing.

**Structs:** `OnePole`, `DCBlocker`, `Biquad`, `SVF`

**Functions:**

| Name | Signature | Docs |
|------|-----------|------|
| `onepole_lowpass` | `(cutoff_hz: f32, rate: SampleRate) -> OnePole` | Create a one-pole lowpass from cutoff frequency |
| `onepole_smooth` | `(time_ms: f32, rate: SampleRate) -> OnePole` | Create a one-pole from smoothing time in milliseconds |
| `onepole_tick` | `(f: OnePole, input: f32) -> OnePole` | Process one sample through the filter |
| `onepole_output` | `(f: OnePole) -> f32` | Get the current output value |
| `onepole_reset` | `(f: OnePole) -> OnePole` | Reset filter state to zero |
| `onepole_set_state` | `(f: OnePole, value: f32) -> OnePole` | Set filter state directly (for initialization) |
| `dcblocker_new` | `(rate: SampleRate) -> DCBlocker` | Create DC blocker (default: ~10Hz cutoff at 44.1kHz) |
| `dcblocker_tick` | `(dc: DCBlocker, input: f32) -> DCBlocker` | Process one sample |
| `dcblocker_output` | `(dc: DCBlocker) -> f32` | Get output |
| `biquad_bypass` | `() -> Biquad` | Create a bypass biquad (passes signal unchanged) |
| `biquad_lowpass` | `(cutoff: f32, q: f32, rate: SampleRate) -> Biquad` | Lowpass filter cutoff: frequency in Hz q: resonance (0.707 = Butterworth, no resonance) |
| `biquad_highpass` | `(cutoff: f32, q: f32, rate: SampleRate) -> Biquad` | Highpass filter |
| `biquad_bandpass` | `(center: f32, q: f32, rate: SampleRate) -> Biquad` | Bandpass filter (constant 0dB peak gain) |
| `biquad_notch` | `(center: f32, q: f32, rate: SampleRate) -> Biquad` | Notch filter (band-reject) |
| `biquad_allpass` | `(center: f32, q: f32, rate: SampleRate) -> Biquad` | All-pass filter (phase shift, no amplitude change) |
| `biquad_tick` | `(f: Biquad, input: f32) -> Biquad` | Process one sample through biquad (Direct Form II Transposed) |
| `biquad_output` | `(f: Biquad) -> f32` | Get the output from last tick (stored in z1 calculation) Note: The actual output should be stored; this is a simplified version |
| `biquad_process` | `(f: Biquad, input: f32) -> f32` | Process and return output in one call (convenience) |
| `biquad_reset` | `(f: Biquad) -> Biquad` | Reset filter state |
| `biquad_set_cutoff` | `(f: Biquad, cutoff: f32, q: f32, rate: SampleRate) -> Biquad` | Update cutoff frequency (recalculates coefficients for lowpass) |
| `svf_new` | `(cutoff: f32, q: f32, rate: SampleRate) -> SVF` | Create SVF from cutoff and Q |
| `svf_tick_lowpass` | `(f: SVF, input: f32) -> SVF` | Process one sample, returns lowpass output |
| `svf_lowpass` | `(f: SVF) -> f32` | Get lowpass output |
| `svf_highpass` | `(f: SVF, input: f32) -> f32` | Get highpass output |
| `svf_bandpass` | `(f: SVF) -> f32` | Get bandpass output |
| `svf_reset` | `(f: SVF) -> SVF` | Reset SVF state |

### `audio/gpu.flow`

Audio GPU Acceleration (Scaffold)  This module defines a simple backend switch to allow CPU/GPU paths.

**Structs:** `AudioComputeBackend`

**Functions:**

| Name | Signature | Docs |
|------|-----------|------|
| `audio_backend_cpu` | `() -> AudioComputeBackend` | — |
| `audio_backend_gpu` | `() -> AudioComputeBackend` | — |
| `audio_backend_is_gpu` | `(b: AudioComputeBackend) -> bool` | — |
| `audio_backend_gpu_available` | `() -> bool` | — |
| `audio_gain_block` | `(b: AudioComputeBackend, buf: AudioBufferF32, gain: f32) -> void` | Gain processing on interleaved buffer |
| `audio_convolution_block` | `(b: AudioComputeBackend, input: AudioBufferF32, impulse: AudioBufferF32) -> void` | Convolution stub (CPU fallback) |
| `audio_fft_block` | `(b: AudioComputeBackend, buf: AudioBufferF32) -> void` | FFT stub (CPU fallback) |

### `audio/graph.flow`

Audio Graph Helpers (High-Level)  Simple, pragmatic effect chains for real-time routing.

**Structs:** `EffectChain`

**Functions:**

| Name | Signature | Docs |
|------|-----------|------|
| `effect_chain_new` | `(rate: SampleRate) -> EffectChain` | — |
| `effect_chain_set_gain_db` | `(c: EffectChain, db: f32) -> EffectChain` | — |
| `effect_chain_set_pan` | `(c: EffectChain, pan: f32) -> EffectChain` | — |
| `effect_chain_enable_lowpass` | `(c: EffectChain, cutoff: f32, q: f32, rate: SampleRate) -> EffectChain` | — |
| `effect_chain_enable_delay` | `(c: EffectChain, time_ms: f32, feedback: f32, mix: f32, rate: SampleRate) -> EffectChain` | — |
| `effect_chain_update` | `(c: EffectChain,
                                    gain_db: f32,
                                    pan: f32,
                                    enable_lowpass: bool,
                                    cutoff: f32,
                                    enable_delay: bool,
                                    delay_ms: f32,
                                    feedback: f32,
                                    mix: f32) -> EffectChain` | — |
| `effect_chain_tick` | `(c: EffectChain, input: Frame) -> EffectChain` | — |
| `effect_chain_output` | `(c: EffectChain) -> Frame` | — |
| `effect_chain_process_interleaved` | `(c: EffectChain, buf: AudioBufferF32) -> EffectChain` | — |
| `effect_chain_process_interleaved_frames` | `(c: EffectChain, buf: AudioBufferF32, frames: i32) -> EffectChain` | — |

### `audio/graph_bus.flow`

Audio Graph with Buses (Parallel Routing)  Fixed-size buses and nodes for predictable real-time performance.

**Structs:** `AudioBus`, `BusNode`, `BusGraph`

**Constants:**

- `BUS_NODE_NONE: i32`
- `BUS_NODE_GAIN: i32`
- `BUS_NODE_LOWPASS: i32`
- `BUS_NODE_DELAY: i32`
- `BUS_NODE_PAN: i32`

**Functions:**

| Name | Signature | Docs |
|------|-----------|------|
| `bus_node_default` | `() -> BusNode` | — |
| `bus_graph_init` | `(rate: SampleRate, buses: array<AudioBus, 8>, nodes: array<BusNode, 64>, scratch: AudioBufferF32) -> BusGraph` | — |
| `bus_graph_free` | `(g: BusGraph) -> void` | — |
| `bus_graph_add_gain` | `(g: BusGraph, input_bus: i32, output_bus: i32, gain_db: f32) -> BusGraph` | — |
| `bus_graph_add_lowpass` | `(g: BusGraph, input_bus: i32, output_bus: i32, cutoff: f32, q: f32) -> BusGraph` | — |
| `bus_graph_add_delay` | `(g: BusGraph, input_bus: i32, output_bus: i32, delay_ms: f32, feedback: f32, mix: f32) -> BusGraph` | — |
| `bus_graph_add_pan` | `(g: BusGraph, input_bus: i32, output_bus: i32, pan: f32) -> BusGraph` | — |
| `bus_graph_clear_buses` | `(g: BusGraph) -> void` | — |
| `bus_graph_process` | `(g: BusGraph, frames: i32) -> BusGraph` | — |

### `audio/graph_scheduler.flow`

Audio Graph Scheduler  Fixed-size node graph with per-node state and block processing.

**Structs:** `AudioNode`, `AudioGraph`

**Constants:**

- `AUDIO_NODE_NONE: i32`
- `AUDIO_NODE_GAIN: i32`
- `AUDIO_NODE_LOWPASS: i32`
- `AUDIO_NODE_DELAY: i32`
- `AUDIO_NODE_PAN: i32`

**Functions:**

| Name | Signature | Docs |
|------|-----------|------|
| `audio_node_default` | `() -> AudioNode` | — |
| `audio_graph_init` | `(rate: SampleRate, nodes: array<AudioNode, 32>) -> AudioGraph` | — |
| `audio_graph_add_gain` | `(g: AudioGraph, gain_db: f32) -> AudioGraph` | — |
| `audio_graph_add_lowpass` | `(g: AudioGraph, cutoff: f32, q: f32) -> AudioGraph` | — |
| `audio_graph_add_delay` | `(g: AudioGraph, delay_ms: f32, feedback: f32, mix: f32) -> AudioGraph` | — |
| `audio_graph_add_pan` | `(g: AudioGraph, pan: f32) -> AudioGraph` | — |
| `audio_graph_process_interleaved` | `(g: AudioGraph, buf: AudioBufferF32, frames: i32) -> AudioGraph` | — |

### `audio/io.flow`

Audio I/O Module (Real-Time)  Cross-platform audio I/O facade. Backend implemented in runtime (C).

**Structs:** `AudioDeviceConfig`, `AudioDevice`

**Constants:**

- `AUDIO_OK: i32`
- `AUDIO_ERR: i32`

**Functions:**

| Name | Signature | Docs |
|------|-----------|------|
| `audio_device_config` | `(sample_rate: i32, channels: i32, frames_per_buffer: i32,
                                    enable_input: bool, enable_output: bool) -> AudioDeviceConfig` | — |
| `audio_device_ok` | `(dev: AudioDevice) -> bool` | — |
| `audio_device_open` | `(config: AudioDeviceConfig) -> AudioDevice` | — |
| `audio_device_start` | `(dev: AudioDevice) -> i32` | — |
| `audio_device_stop` | `(dev: AudioDevice) -> i32` | — |
| `audio_device_close` | `(dev: AudioDevice) -> void` | — |
| `audio_read_f32` | `(dev: AudioDevice, out: ptr<f32>, frames: i32) -> i32` | Read interleaved f32 frames into out buffer. Returns frames read. |
| `audio_write_f32` | `(dev: AudioDevice, input: ptr<f32>, frames: i32) -> i32` | Write interleaved f32 frames from input buffer. Returns frames written. |
| `audio_available_read` | `(dev: AudioDevice) -> i32` | — |
| `audio_available_write` | `(dev: AudioDevice) -> i32` | — |
| `audio_last_error` | `(dev: AudioDevice) -> string` | — |
| `audio_probe_devices` | `() -> string` | — |
| `audio_device_has_input` | `(dev: AudioDevice) -> bool` | — |
| `audio_device_has_output` | `(dev: AudioDevice) -> bool` | — |

### `audio/lattice_allpass.flow`

Many-pole lattice all-pass — Schur reflections, fast per-sample modulation Import: import "stdlib/audio/lattice_allpass.flow"

**Structs:** `LatticeAllpass`, `LatticeAllpassDesign`

**Functions:**

| Name | Signature | Docs |
|------|-----------|------|
| `lattice_allpass_design_from_poles` | `(
    poles: ptr<f64>,
    pole_count: i32,
    a_buf: ptr<f64>,
    ctrl_buf: ptr<f64>,
    apow_buf: ptr<f64>,
    blk_buf: ptr<f64>,
    na_buf: ptr<f64>
) -> LatticeAllpassDesign` | — |
| `lattice_allpass_new` | `(
    design: LatticeAllpassDesign,
    mod_depth: f32,
    mod_rate_hz: f32
) -> LatticeAllpass` | — |
| `lattice_allpass_modulate` | `(ap: LatticeAllpass, rate: SampleRate) -> LatticeAllpass` | Retune reflections from GA/WFC-style modulation signal (per-pole phase offsets). |
| `lattice_allpass_tick` | `(ap: LatticeAllpass, input: f32) -> LatticeAllpass` | Cascade all-pass sections H_i(z)=(k_i+z^{-1})/(1+k_i z^{-1}); g[2i]=x_prev, g[2i+1]=y_prev. |
| `lattice_allpass_output` | `(ap: LatticeAllpass) -> f32` | — |
| `lattice_allpass_reset` | `(ap: LatticeAllpass) -> LatticeAllpass` | — |
| `lattice_allpass_block_energy` | `(samples: ptr<f32>, count: i32) -> f32` | Energy metric for all-pass verification (should stay near input RMS). |

### `audio/livecode.flow`

Livecode Module - Ultra-Easy Audio Programming  THE EASIEST WAY TO MAKE SOUND IN ANY PROGRAMMING LANGUAGE.

**Structs:** `LiveContext`

**Functions:**

| Name | Signature | Docs |
|------|-----------|------|
| `live_context_new` | `() -> LiveContext` | — |
| `live_context_44k_120bpm` | `() -> LiveContext` | — |
| `bass` | `(note: i32) -> f32` | Play a bass note |
| `lead` | `(note: i32) -> f32` | Play a lead note |
| `pad` | `(note: i32) -> f32` | Play a pad note |
| `pluck` | `(note: i32) -> f32` | Play a pluck note |
| `organ` | `(note: i32) -> f32` | Play an organ note |
| `kick` | `() -> f32` | Kick drum (808-style) |
| `snare` | `() -> f32` | Snare drum |
| `hat` | `() -> f32` | Hi-hat (closed) |
| `hat_open` | `() -> f32` | Hi-hat (open) |
| `clap` | `() -> f32` | Clap |
| `kick_on_beat` | `(clock: Clock, pos: i64) -> bool` | Is kick happening on this beat? |
| `snare_on_backbeat` | `(clock: Clock, pos: i64) -> bool` | Is snare happening on backbeat? (beats 2 and 4 in 4/4) |
| `hat_on_eighth` | `(clock: Clock, pos: i64) -> bool` | Is hi-hat happening on eighth notes? |
| `hat_on_sixteenth` | `(clock: Clock, pos: i64) -> bool` | Is hi-hat happening on sixteenth notes? |
| `pattern_4` | `(notes: array<i32, 4>, clock: Clock, pos: i64) -> f32` | Play a repeating pattern of notes |
| `pattern_8` | `(notes: array<i32, 8>, clock: Clock, pos: i64) -> f32` | Play a repeating 8-step pattern |
| `chord_progression` | `(chords: array<array<i32, 3>, 4>, clock: Clock, pos: i64) -> f32` | Play a chord progression (changes every bar) |
| `euclidean_hit` | `(k: i32, n: i32, step_val: i32) -> bool` | Generate a euclidean rhythm pattern (k hits in n steps) Example: euclidean_hit(3, 8, step) gives [x . . x . . x .] |
| `euclidean_pattern` | `(k: i32, n: i32, clock: Clock, pos: i64) -> f32` | Play euclidean rhythm with instrument |
| `scale_note` | `(root: i32, scale_type: i32, degree: i32) -> i32` | Play a note from a scale by degree (0-6) |
| `with_delay` | `(input: f32, clock: Clock) -> f32` | Add delay to a signal |
| `with_distortion` | `(input: f32, amount: f32) -> f32` | Add distortion to a signal |
| `with_reverb` | `(input: f32, size: f32) -> f32` | Add reverb to a signal |
| `with_bitcrush` | `(input: f32, bits: i32) -> f32` | Add bitcrushing to a signal |
| `house_beat` | `(clock: Clock, pos: i64) -> f32` | 4-on-the-floor house beat |
| `bass_pattern_simple` | `(root: i32, clock: Clock, pos: i64) -> f32` | Basic bassline (root note pattern) |
| `arpeggio` | `(chord: array<i32, 3>, clock: Clock, pos: i64) -> f32` | Arpeggio pattern |
| `master_out` | `(input: f32) -> f32` | Clip and normalize output |
| `master_out_stereo` | `(left: f32, right: f32) -> Frame` | Stereo output |

### `audio/notation.flow`

Musical Notation Module - Load Music from Files  Simple text-based notation for livecoding:

**Effects:** `Notation`

**Structs:** `MusicNote`, `NotationReader`

**Functions:**

| Name | Signature | Docs |
|------|-----------|------|
| `parse_note_name` | `(name: string) -> i32` | Parse note name to MIDI number (e.g., "C4" -> 60) |
| `parse_note_simple` | `(note_str: string, duration: i32) -> MusicNote` | Helper: Parse a single note/duration pair Format: "C4/4" means C4 for 4 sixteenth notes (quarter note) |
| `notation_reader_new` | `() -> NotationReader` | — |
| `notation_load_file` | `(reader: ptr<NotationReader>, path: string) -> bool` | Regular functions (effect impl not fully supported in C backend yet) |
| `load_file` | `(reader: ptr<NotationReader>, path: string) -> bool` | — |
| `get_note_count` | `(reader: ptr<NotationReader>) -> i32` | — |
| `get_note` | `(reader: ptr<NotationReader>, idx: i32) -> MusicNote` | — |
| `parse_line` | `(reader: ptr<NotationReader>, line: string) -> bool` | — |
| `load_notation` | `(path: string) -> NotationReader` | Create a notation reader and load a file |
| `note_name_to_midi` | `(note: i32, octave: i32) -> i32` | Convert note name to MIDI (manual mapping for now) |
| `note_from_name` | `(name: i32, octave: i32, duration: i32) -> MusicNote` | Quick note constructors |

### `audio/oscillators.flow`

Audio Oscillators Module  Phase-based oscillators and waveshaping functions.

**Structs:** `Phasor`, `NoiseState`, `LFO`

**Constants:**

- `TWO_PI: f64`
- `PI: f64`

**Functions:**

| Name | Signature | Docs |
|------|-----------|------|
| `phasor_new` | `(freq: f64, rate: SampleRate) -> Phasor` | Create a phasor for a given frequency and sample rate |
| `phasor_new_with_phase` | `(freq: f64, rate: SampleRate, initial_phase: f64) -> Phasor` | Create a phasor with initial phase |
| `phasor_tick` | `(p: Phasor) -> Phasor` | Advance the phasor by one sample (returns new state) |
| `phasor_value` | `(p: Phasor) -> f64` | Get current phase value [0.0, 1.0) |
| `phasor_set_freq` | `(p: Phasor, freq: f64, rate: SampleRate) -> Phasor` | Set frequency (returns new phasor with updated increment) |
| `phasor_reset` | `(p: Phasor) -> Phasor` | Reset phase to zero |
| `phasor_sync` | `(p: Phasor, target_phase: f64) -> Phasor` | Sync to another phasor's phase |
| `sine` | `(phase: f64) -> f32` | Sine wave: sin(2π * phase) |
| `saw` | `(phase: f64) -> f32` | Saw wave: 2 * phase - 1 (naive, has aliasing at high frequencies) |
| `saw_reverse` | `(phase: f64) -> f32` | Reverse saw (ramp down) |
| `square` | `(phase: f64) -> f32` | Square wave: phase < 0.5 ? 1.0 : -1.0 (naive, has aliasing) |
| `pulse` | `(phase: f64, width: f64) -> f32` | Pulse wave with variable width [0.0, 1.0] |
| `triangle` | `(phase: f64) -> f32` | Triangle wave: 4 * \|phase - 0.5\| - 1 |
| `saw_blep` | `(phase: f64, increment: f64) -> f32` | Band-limited saw using PolyBLEP |
| `square_blep` | `(phase: f64, increment: f64) -> f32` | Band-limited square using PolyBLEP |
| `noise_new` | `(seed: i64) -> NoiseState` | Create noise generator with seed |
| `noise_tick` | `(n: NoiseState) -> NoiseState` | Generate next random sample and update state |
| `noise_value` | `(n: NoiseState) -> f32` | Get current noise value [-1.0, 1.0] |
| `white_noise` | `(n: NoiseState) -> f32` | White noise (calls tick internally - stateful convenience) |
| `lfo_new` | `(rate_hz: f64, sample_rate: SampleRate, depth: f32) -> LFO` | Create an LFO |
| `lfo_tick` | `(l: LFO) -> LFO` | Tick the LFO |
| `lfo_sine` | `(l: LFO) -> f32` | Get sine LFO value (bipolar: -depth to +depth) |
| `lfo_triangle` | `(l: LFO) -> f32` | Get triangle LFO value |
| `lfo_unipolar` | `(l: LFO) -> f32` | Get unipolar LFO value [0, depth] |

### `audio/processor.flow`

Audio Processor Module  Trait-based interface for audio processing components.

**Structs:** `GainProcessor`, `HardClipper`, `SoftClipper`, `DCOffset`, `StereoWidth`, `StereoPan`

**Functions:**

| Name | Signature | Docs |
|------|-----------|------|
| `gain_processor_new` | `(gain_db: f32) -> GainProcessor` | — |
| `gain_processor_set_db` | `(g: GainProcessor, db: f32) -> GainProcessor` | Set gain in dB |
| `gain_processor_set_linear` | `(g: GainProcessor, linear: f32) -> GainProcessor` | Set gain as linear multiplier |
| `hard_clipper_new` | `(threshold: f32) -> HardClipper` | — |
| `soft_clipper_new` | `(drive: f32) -> SoftClipper` | — |
| `dc_offset_new` | `(offset: f32) -> DCOffset` | — |
| `stereo_width_new` | `(width: f32) -> StereoWidth` | — |
| `stereo_pan_new` | `(pan: f32) -> StereoPan` | — |
| `process_with_gain_clip` | `(sample: f32, gain: f32, threshold: f32) -> f32` | Process a mono sample through gain and clip |
| `crossfade` | `(a: f32, b: f32, mix: f32) -> f32` | Mix two signals with crossfade (0.0 = all A, 1.0 = all B) |
| `crossfade_equal_power` | `(a: f32, b: f32, mix: f32) -> f32` | Equal power crossfade (smoother for audio) |

### `audio/scales.flow`

Music Theory Module - Scales, Chords, and Note Helpers  Makes music theory incredibly easy - easier than any other language.

**Functions:**

| Name | Signature | Docs |
|------|-----------|------|
| `note_to_midi` | `(note_name: string) -> i32` | Convert note name to MIDI number "C4" = 60 (middle C), "A4" = 69 (concert A = 440Hz) Supports: C, C#, Db, D, D#, Eb, E, F, F#, Gb, G, G#, Ab, A, A#, Bb, B |
| `note_C` | `(octave: i32) -> i32` | Quick note constructors for common notes |
| `note_Cs` | `(octave: i32) -> i32` | — |
| `note_Db` | `(octave: i32) -> i32` | — |
| `note_D` | `(octave: i32) -> i32` | — |
| `note_Ds` | `(octave: i32) -> i32` | — |
| `note_Eb` | `(octave: i32) -> i32` | — |
| `note_E` | `(octave: i32) -> i32` | — |
| `note_F` | `(octave: i32) -> i32` | — |
| `note_Fs` | `(octave: i32) -> i32` | — |
| `note_Gb` | `(octave: i32) -> i32` | — |
| `note_G` | `(octave: i32) -> i32` | — |
| `note_Gs` | `(octave: i32) -> i32` | — |
| `note_Ab` | `(octave: i32) -> i32` | — |
| `note_A` | `(octave: i32) -> i32` | — |
| `note_As` | `(octave: i32) -> i32` | — |
| `note_Bb` | `(octave: i32) -> i32` | — |
| `note_B` | `(octave: i32) -> i32` | — |
| `C4` | `() -> i32` | Common note shortcuts |
| `A4` | `() -> i32` | — |
| `C3` | `() -> i32` | — |
| `C5` | `() -> i32` | — |
| `scale_major` | `(root: i32) -> array<i32, 7>` | Scale intervals (semitones from root) Major: W W H W W W H (2 2 1 2 2 2 1) |
| `scale_minor` | `(root: i32) -> array<i32, 7>` | Natural minor: W H W W H W W (2 1 2 2 1 2 2) |
| `scale_pentatonic_major` | `(root: i32) -> array<i32, 5>` | Pentatonic major: C D E G A (5 notes) |
| `scale_pentatonic_minor` | `(root: i32) -> array<i32, 5>` | Pentatonic minor: C Eb F G Bb (5 notes) |
| `scale_blues` | `(root: i32) -> array<i32, 6>` | Blues scale: C Eb F F# G Bb (6 notes) |
| `scale_chromatic` | `(root: i32) -> array<i32, 12>` | Chromatic scale (all 12 notes) |
| `scale_whole_tone` | `(root: i32) -> array<i32, 6>` | Whole tone scale: C D E F# G# A# (6 notes, all whole steps) |
| `scale_dorian` | `(root: i32) -> array<i32, 7>` | Dorian mode: D E F G A B C (minor with raised 6th) |
| `scale_phrygian` | `(root: i32) -> array<i32, 7>` | Phrygian mode: E F G A B C D (minor with lowered 2nd) |
| `scale_lydian` | `(root: i32) -> array<i32, 7>` | Lydian mode: F G A B C D E (major with raised 4th) |
| `scale_mixolydian` | `(root: i32) -> array<i32, 7>` | Mixolydian mode: G A B C D E F (major with lowered 7th) |
| `chord_major` | `(root: i32) -> array<i32, 3>` | Major triad: C E G (root, major 3rd, perfect 5th) |
| `chord_minor` | `(root: i32) -> array<i32, 3>` | Minor triad: C Eb G (root, minor 3rd, perfect 5th) |
| `chord_dim` | `(root: i32) -> array<i32, 3>` | Diminished triad: C Eb Gb |
| `chord_aug` | `(root: i32) -> array<i32, 3>` | Augmented triad: C E G# |
| `chord_maj7` | `(root: i32) -> array<i32, 4>` | Major 7th: C E G B |
| `chord_min7` | `(root: i32) -> array<i32, 4>` | Minor 7th: C Eb G Bb |
| `chord_dom7` | `(root: i32) -> array<i32, 4>` | Dominant 7th: C E G Bb |
| `chord_sus2` | `(root: i32) -> array<i32, 3>` | Suspended 2nd: C D G |
| `chord_sus4` | `(root: i32) -> array<i32, 3>` | Suspended 4th: C F G |
| `chord_power` | `(root: i32) -> array<i32, 2>` | Power chord (rock): C G (root + perfect 5th) |
| `midi_to_freq_accurate` | `(note: i32) -> f32` | Get frequency for a MIDI note (more accurate than stdlib/audio.flow version) |
| `freq` | `(midi_note: i32) -> f32` | Shorthand: get frequency from MIDI note |
| `progression_145` | `(root: i32) -> array<array<i32, 3>, 4>` | Common chord progression: I - IV - V - I (in major key) |
| `progression_pop` | `(root: i32) -> array<array<i32, 3>, 4>` | Pop progression: I - V - vi - IV (e.g., C - G - Am - F) |
| `progression_blues` | `(root: i32) -> array<array<i32, 3>, 4>` | Blues progression: I - IV - I - V (12-bar simplified) |
| `transpose` | `(note: i32, semitones: i32) -> i32` | Transpose a MIDI note by semitones |
| `octave_up` | `(note: i32) -> i32` | Octave shift |
| `octave_down` | `(note: i32) -> i32` | — |
| `chord_invert` | `(chord: array<i32, 3>) -> array<i32, 3>` | Invert a chord (move lowest note up an octave) |
| `is_in_scale` | `(note: i32, scale: array<i32, 7>) -> bool` | Check if note is in scale (basic check for 7-note scales) |

### `audio/simd.flow`

Audio SIMD Helpers  Portable loops live here; the always-linked Flow runtime module

**Functions:**

| Name | Signature | Docs |
|------|-----------|------|
| `audio_gain_interleaved_f32` | `(data: ptr<f32>, frames: i32, channels: i32, gain: f32) -> void` | Portable implementation (no external link required) |
| `audio_gain_interleaved_f32_fast` | `(data: ptr<f32>, frames: i32, channels: i32, gain: f32) -> void` | Optional fast path (lib/runtime/audio_simd.flow, always linked by ./flow run) |
| `audio_mix_interleaved_f32` | `(dst: ptr<f32>, src: ptr<f32>, frames: i32, channels: i32) -> void` | — |
| `audio_copy_interleaved_f32` | `(dst: ptr<f32>, src: ptr<f32>, frames: i32, channels: i32) -> void` | — |
| `audio_mix_interleaved_f32_fast` | `(dst: ptr<f32>, src: ptr<f32>, frames: i32, channels: i32) -> void` | — |
| `audio_copy_interleaved_f32_fast` | `(dst: ptr<f32>, src: ptr<f32>, frames: i32, channels: i32) -> void` | — |

### `audio/synth.flow`

Synth Presets Module - Ready-to-Use Instruments  Pre-configured synthesizers that sound good out of the box.

**Structs:** `Synth`, `ADSREnvelope`

**Functions:**

| Name | Signature | Docs |
|------|-----------|------|
| `synth_bass` | `() -> Synth` | Deep bass synth - thick and powerful |
| `synth_lead` | `() -> Synth` | Lead synth - bright and cutting |
| `synth_pad` | `() -> Synth` | Pad synth - lush and atmospheric |
| `synth_pluck` | `() -> Synth` | Pluck synth - percussive and bright |
| `synth_organ` | `() -> Synth` | Organ synth - classic tone wheel sound |
| `synth_fm` | `() -> Synth` | FM synth - digital and metallic |
| `synth_sub` | `() -> Synth` | Sub bass - deep rumble |
| `synth_brass` | `() -> Synth` | Brass synth - punchy and bright |
| `synth_tick` | `(synth: Synth, freq: f32, gate: bool) -> f32` | Generate one sample from the synth |

### `audio.flow`

Audio Module - Core Types and Operations  Real-time audio processing primitives with proper DSP nomenclature.

**Structs:** `SampleRate`, `Samples`, `Seconds`, `Frame`, `Layout`, `Buffer`, `AudioBufferF32`

**Functions:**

| Name | Signature | Docs |
|------|-----------|------|
| `sample_rate_new` | `(hz: f64) -> SampleRate` | Constructors |
| `samples_new` | `(count: i64) -> Samples` | — |
| `seconds_new` | `(value: f64) -> Seconds` | — |
| `sample_rate_44100` | `() -> SampleRate` | Common sample rates |
| `sample_rate_48000` | `() -> SampleRate` | — |
| `sample_rate_96000` | `() -> SampleRate` | — |
| `samples_to_seconds` | `(s: Samples, rate: SampleRate) -> Seconds` | Convert samples to seconds: samples / sample_rate |
| `seconds_to_samples` | `(t: Seconds, rate: SampleRate) -> Samples` | Convert seconds to samples: seconds * sample_rate (rounded) |
| `samples_per_ms` | `(rate: SampleRate) -> f64` | Get samples per millisecond |
| `ms_to_samples` | `(ms: f64, rate: SampleRate) -> Samples` | Convert milliseconds to samples |
| `frame_new` | `(left: f32, right: f32) -> Frame` | Create a stereo frame |
| `frame_mono` | `(value: f32) -> Frame` | Create a mono frame (same value both channels) |
| `frame_zero` | `() -> Frame` | Create a silent frame |
| `frame_mix` | `(a: Frame, b: Frame) -> Frame` | Mix two frames together |
| `frame_scale` | `(f: Frame, gain: f32) -> Frame` | Scale a frame by a gain value |
| `frame_pan` | `(value: f32, pan: f32) -> Frame` | Pan a mono signal (-1.0 = full left, 0.0 = center, 1.0 = full right) |
| `frame_to_mono` | `(f: Frame) -> f32` | Convert stereo to mono (average) |
| `layout_interleaved` | `() -> Layout` | — |
| `layout_planar` | `() -> Layout` | — |
| `buffer_create` | `(frames: i32, channels: i32) -> Buffer` | Create a buffer descriptor |
| `audio_buffer_empty_f32` | `() -> AudioBufferF32` | — |
| `audio_buffer_alloc_f32` | `(frames: i32, channels: i32, layout: Layout) -> AudioBufferF32` | — |
| `audio_buffer_free_f32` | `(buf: AudioBufferF32) -> void` | — |
| `audio_buffer_index` | `(buf: AudioBufferF32, frame: i32, channel: i32) -> i32` | — |
| `audio_buffer_get_f32` | `(buf: AudioBufferF32, frame: i32, channel: i32) -> f32` | — |
| `audio_buffer_set_f32` | `(buf: AudioBufferF32, frame: i32, channel: i32, value: f32) -> void` | — |
| `audio_buffer_zero_f32` | `(buf: AudioBufferF32) -> void` | — |
| `audio_buffer_copy_interleaved_f32` | `(dst: AudioBufferF32, src: AudioBufferF32, frames: i32) -> void` | — |
| `audio_buffer_add_interleaved_f32` | `(dst: AudioBufferF32, src: AudioBufferF32, frames: i32) -> void` | — |
| `audio_buffer_frame_count` | `(buf: AudioBufferF32) -> i32` | — |
| `audio_buffer_channel_count` | `(buf: AudioBufferF32) -> i32` | — |
| `buffer_stereo` | `(frames: i32) -> Buffer` | Create a stereo buffer (most common case) |
| `buffer_mono` | `(frames: i32) -> Buffer` | Create a mono buffer |
| `buffer_sample_count` | `(buf: Buffer) -> i32` | Get total sample count (frames * channels) |
| `buffer_duration` | `(buf: Buffer, rate: SampleRate) -> Seconds` | Get buffer duration in seconds |
| `linear_to_db` | `(linear: f32) -> f32` | Convert linear amplitude to decibels 1.0 -> 0dB, 0.5 -> -6dB, 0.0 -> -infinity (clamped to -96dB) |
| `db_to_linear` | `(db: f32) -> f32` | Convert decibels to linear amplitude 0dB -> 1.0, -6dB -> 0.5, -96dB -> ~0.0 |
| `midi_to_freq` | `(note: i32) -> f32` | MIDI note to frequency (A4 = 69 = 440Hz) |
| `freq_to_period_samples` | `(freq: f32, rate: SampleRate) -> f32` | Frequency to period in samples |
| `clip` | `(sample: f32) -> f32` | Hard clip a sample to [-1.0, 1.0] |
| `soft_clip` | `(sample: f32) -> f32` | Soft clip using tanh-like curve (warmer saturation) |
| `frame_clip` | `(f: Frame) -> Frame` | Clip a frame |

### `autodiff.flow`

FLOW Automatic Differentiation Library  Two modes:

**Functions:**

| Name | Signature | Docs |
|------|-----------|------|
| `dual_var` | `(x: f32) -> Dual` | Seed forward-mode AD: Dual(x, 1) so ∂/∂x propagates. |
| `dual_const` | `(x: f32) -> Dual` | Lift a constant into Dual space: Dual(x, 0). |
| `dual_add` | `(a: Dual, b: Dual) -> Dual` | Dual addition: (a+b, a'+b'). |
| `dual_sub` | `(a: Dual, b: Dual) -> Dual` | Dual subtraction: (a-b, a'-b'). |
| `dual_mul` | `(a: Dual, b: Dual) -> Dual` | Dual multiply via product rule: (ab, a'b + ab'). |
| `dual_div` | `(a: Dual, b: Dual) -> Dual` | Dual divide via quotient rule: a/b with derivative (a'b - ab')/b². |
| `dual_pow` | `(x: Dual, n: f32) -> Dual` | Dual power x^n for constant n: derivative n x^{n-1} x'. |
| `dual_sq` | `(x: Dual) -> Dual` | Dual square x² with derivative 2x x'. |
| `dual_sqrt` | `(x: Dual) -> Dual` | Dual square root √x; domain x.val > 0. |
| `dual_exp` | `(x: Dual) -> Dual` | Dual exponential e^x with derivative e^x x'. |
| `dual_log` | `(x: Dual) -> Dual` | Dual natural log ln(x); domain x.val > 0. |
| `dual_sin` | `(x: Dual) -> Dual` | Dual sine (radians): (sin x, cos(x) x'). |
| `dual_cos` | `(x: Dual) -> Dual` | Dual cosine (radians): (cos x, -sin(x) x'). |
| `dual_tan` | `(x: Dual) -> Dual` | Dual tangent (radians): derivative x' / cos²(x). |
| `dual_relu` | `(x: Dual) -> Dual` | Dual ReLU: max(0,x); gradient is 0 for x <= 0. |
| `dual_sigmoid` | `(x: Dual) -> Dual` | Dual sigmoid σ(x)=1/(1+e^{-x}); derivative σ(1-σ)x'. |
| `dual_tanh` | `(x: Dual) -> Dual` | Dual tanh; derivative (1 - tanh²x) x'. |
| `numerical_grad` | `(f_plus: f32, f_minus: f32, epsilon: f32) -> f32` | Central finite-difference gradient: (f+ - f-) / (2ε). Useful for checking autodiff implementations. |
| `dual_val` | `(d: Dual) -> f32` | Extract primal value from a Dual. |
| `dual_grad` | `(d: Dual) -> f32` | Extract forward-mode derivative (tangent) from a Dual. |
| `dx` | `(x: f32) -> Dual` | Alias for dual_var: Dual(x, 1). |
| `d` | `(x: f32) -> Dual` | Alias for dual_const: Dual(x, 0). |
| `add` | `(a: Dual, b: Dual) -> Dual` | Overloaded Dual+Dual addition with forward gradients. |
| `add` | `(a: Dual, b: f32) -> Dual` | Add Dual and scalar constant. |
| `add` | `(a: f32, b: Dual) -> Dual` | Add scalar constant and Dual. |
| `sub` | `(a: Dual, b: Dual) -> Dual` | Overloaded Dual−Dual subtraction with forward gradients. |
| `sub` | `(a: Dual, b: f32) -> Dual` | Subtract scalar from Dual. |
| `sub` | `(a: f32, b: Dual) -> Dual` | Subtract Dual from scalar (gradient negated). |
| `mul` | `(a: Dual, b: Dual) -> Dual` | Overloaded Dual×Dual multiply (product rule). |
| `mul` | `(a: Dual, b: f32) -> Dual` | Scale Dual by scalar. |
| `mul` | `(a: f32, b: Dual) -> Dual` | Scale Dual by scalar (left multiply). |
| `div` | `(a: Dual, b: Dual) -> Dual` | Dual÷Dual division (quotient rule). Prefer this name for operator `/` sugar. |
| `ddiv` | `(a: Dual, b: Dual) -> Dual` | Dual÷Dual division (quotient rule); legacy name ddiv. |
| `div` | `(a: Dual, b: f32) -> Dual` | Divide Dual by scalar. |
| `divs` | `(a: Dual, b: f32) -> Dual` | Divide Dual by scalar; named divs to avoid C div conflict historically. |
| `div` | `(a: f32, b: Dual) -> Dual` | Divide scalar by Dual (reciprocal-style quotient rule). |
| `rdiv` | `(a: f32, b: Dual) -> Dual` | Divide scalar by Dual; legacy name rdiv. |
| `addc` | `(a: f32, b: Dual) -> Dual` | Legacy alias: scalar + Dual. |
| `rsub` | `(a: f32, b: Dual) -> Dual` | Legacy alias: scalar − Dual. |
| `smul` | `(a: f32, b: Dual) -> Dual` | Legacy alias: scalar × Dual. |
| `scale` | `(a: f32, b: Dual) -> Dual` | Scale Dual by scalar (alias of mul). |
| `add` | `(a: f32, b: f32) -> f32` | Scalar addition (overload for mixed Dual expressions). |
| `sub` | `(a: f32, b: f32) -> f32` | Scalar subtraction overload. |
| `mul` | `(a: f32, b: f32) -> f32` | Scalar multiplication overload. |
| `neg` | `(a: Dual) -> Dual` | Negate Dual value and gradient. |
| `sigmoid` | `(x: Dual) -> Dual` | Short alias for dual_sigmoid. |
| `ln` | `(x: Dual) -> Dual` | Short alias for dual_log (natural logarithm). |
| `log` | `(x: Dual) -> Dual` | Alias of ln / dual_log on Dual. |
| `e` | `(x: Dual) -> Dual` | Short alias for dual_exp. |
| `sinD` | `(x: Dual) -> Dual` | Dual sine alias (avoids shadowing C sin). |
| `cosD` | `(x: Dual) -> Dual` | Dual cosine alias (avoids shadowing C cos). |
| `tanhD` | `(x: Dual) -> Dual` | Dual tanh alias (avoids shadowing C tanh). |
| `sq` | `(x: Dual) -> Dual` | Dual square x². |
| `cube` | `(x: Dual) -> Dual` | Dual cube x³. |
| `pow4` | `(x: Dual) -> Dual` | Dual fourth power x⁴. |
| `sq_diff` | `(x: Dual, c: f32) -> Dual` | Squared residual (x − c)² for constant c. |
| `linear` | `(x: Dual, a: f32, b: f32) -> Dual` | Affine map a*x + b on Dual. |
| `quadratic` | `(x: Dual, a: f32, b: f32, c: f32) -> Dual` | Quadratic a*x² + b*x + c on Dual. |
| `sin_scaled` | `(x: Dual, a: f32) -> Dual` | Dual sin(a*x) for constant scale a. |
| `cos_scaled` | `(x: Dual, a: f32) -> Dual` | Dual cos(a*x) for constant scale a. |
| `exp_scaled` | `(x: Dual, a: f32) -> Dual` | Dual exp(a*x) for constant scale a. |
| `chain_add` | `(f: Dual, g: Dual) -> Dual` | Chain helper: Dual sum f + g. |
| `chain_mul` | `(f: Dual, g: Dual) -> Dual` | Chain helper: Dual product f * g. |
| `weighted_sum` | `(f: Dual, a: f32, g: Dual, b: f32) -> Dual` | Weighted Dual sum: a*f + b*g. |
| `sum3` | `(a: Dual, b: Dual, c: Dual) -> Dual` | Sum of three Dual values (and their gradients). |

### `autodiff_reverse.flow`

Reverse-Mode Automatic Differentiation Helpers  Provides operations that return both value AND local gradient,

**Functions:**

| Name | Signature | Docs |
|------|-----------|------|
| `op_add` | `(a: f32, b: f32) -> BinaryResult` | a+b with local grads (1, 1) for reverse-mode backprop. |
| `op_sub` | `(a: f32, b: f32) -> BinaryResult` | a−b with local grads (1, −1). |
| `op_mul` | `(a: f32, b: f32) -> BinaryResult` | a*b with local grads (b, a) via product rule. |
| `op_div` | `(a: f32, b: f32) -> BinaryResult` | a/b with local grads (1/b, −a/b²). |
| `op_sq` | `(x: f32) -> UnaryResult` | x² with local grad 2x. |
| `op_sqrt` | `(x: f32) -> UnaryResult` | √x with local grad 1/(2√x); domain x > 0. |
| `op_exp` | `(x: f32) -> UnaryResult` | e^x with local grad e^x. |
| `op_log` | `(x: f32) -> UnaryResult` | ln(x) with local grad 1/x; domain x > 0. |
| `op_sigmoid` | `(x: f32) -> UnaryResult` | Sigmoid σ(x) with local grad σ(1−σ). |
| `op_sin` | `(x: f32) -> UnaryResult` | sin(x) with local grad cos(x). |
| `op_cos` | `(x: f32) -> UnaryResult` | cos(x) with local grad −sin(x). |
| `op_tanh` | `(x: f32) -> UnaryResult` | tanh(x) with local grad 1 − tanh²(x). |
| `op_relu` | `(x: f32) -> UnaryResult` | ReLU max(0,x) with local grad 1 if x>0 else 0. |
| `op_neg` | `(x: f32) -> UnaryResult` | Negation −x with local grad −1. |

### `blas.flow`

BLAS/LAPACK bindings via Apple Accelerate (or OpenBLAS on Linux) Import: import "stdlib/blas.flow"

**Functions:**

| Name | Signature | Docs |
|------|-----------|------|
| `mat_new` | `(rows: i32, cols: i32) -> Mat` | Allocate a zero-filled rows×cols matrix (row-major f64). Caller must mat_free. |
| `mat_free` | `(m: Mat) -> void` | Free matrix storage if owned (owns == 1); no-op for wrapped views. |
| `mat_wrap` | `(data: ptr<f64>, rows: i32, cols: i32) -> Mat` | Wrap existing row-major buffer as Mat without taking ownership. |
| `mat_clone` | `(m: Mat) -> Mat` | Deep-copy matrix into a new owned Mat. |
| `mat_get` | `(m: Mat, i: i32, j: i32) -> f64` | Read element m[i, j] (0-based, row-major). |
| `mat_set` | `(m: Mat, i: i32, j: i32, val: f64) -> void` | Write element m[i, j] = val (0-based, row-major). |
| `gemm` | `(A: Mat, B: Mat, C: Mat) -> void` | Matrix product via BLAS dgemm: C = A @ B. Shapes: A (m×k), B (k×n), C (m×n). Overwrites C. |
| `gemm_alpha_beta` | `(alpha: f64, A: Mat, B: Mat, beta: f64, C: Mat) -> void` | Scaled GEMM: C = alpha * A @ B + beta * C (BLAS dgemm). |
| `gemv` | `(A: Mat, x: ptr<f64>, y: ptr<f64>) -> void` | Matrix-vector product via BLAS dgemv: y = A @ x. |
| `dot` | `(x: ptr<f64>, y: ptr<f64>, n: i32) -> f64` | Dot product of length-n vectors via BLAS ddot: x · y. |
| `norm2` | `(x: ptr<f64>, n: i32) -> f64` | Euclidean 2-norm of length-n vector via BLAS dnrm2: \|\|x\|\|_2. |
| `axpy` | `(alpha: f64, x: ptr<f64>, y: ptr<f64>, n: i32) -> void` | BLAS daxpy: y = alpha * x + y (in-place on y). |
| `scal` | `(alpha: f64, x: ptr<f64>, n: i32) -> void` | BLAS dscal: scale vector in place, x = alpha * x. |
| `solve` | `(A: Mat, b: ptr<f64>, x: ptr<f64>) -> i32` | Solve A x = b via LAPACK dgesv (LU). Writes solution to x. Returns 0 on success; non-zero info on failure. A is not modified. |
| `getrf` | `(A: Mat, pivots: ptr<i32>) -> i32` | In-place LU factorization via LAPACK dgetrf. Overwrites A with L/U factors. pivots must point at at least min(A.rows, A.cols) i32 slots (max 1024 here). Returns LAPACK info (0 = success). |
| `lu_factor` | `(A: Mat, pivots: ptr<i32>) -> i32` | Alias for getrf — matches pattern-adoption sketch naming. |
| `matmul` | `(A: Mat, B: Mat) -> Mat` | Allocate and return C = A @ B (caller must mat_free C). |
| `transpose` | `(A: Mat) -> Mat` | Return a new matrix that is the transpose of A. |
| `eye` | `(n: i32) -> Mat` | n×n identity matrix (ones on diagonal). |
| `zeros` | `(rows: i32, cols: i32) -> Mat` | rows×cols zero matrix (alias for mat_new). |
| `ones` | `(rows: i32, cols: i32) -> Mat` | rows×cols matrix filled with 1.0. |

### `collections.flow`

FLOW Collections Standard Library HashMap, Set, Queue, Stack, Vector

*No `export` items found (internal / extern-only module).*

### `concurrent.flow`

FLOW Concurrency Standard Library Threads, mutexes, channels, atomics — real pthread/atomic backends. See docs/language/concurrency-vs-go.md

*No `export` items found (internal / extern-only module).*

### `crypto.flow`

Cryptographic primitives (FFI to platform or bundled implementations)

*No `export` items found (internal / extern-only module).*

### `dynamics/attractor.flow`

Attractors & nonlinear flows (indexed vector fields + RK4) Import: import "stdlib/dynamics/attractor.flow"

*No `export` items found (internal / extern-only module).*

### `dynamics/core.flow`

Dynamical system DSL types (declarative struct syntax) Import: import "stdlib/dynamics/core.flow"

*No `export` items found (internal / extern-only module).*

### `dynamics/ga.flow`

Genetic algorithm for feedback gain search Import: import "stdlib/dynamics/ga.flow"

*No `export` items found (internal / extern-only module).*

### `dynamics/ga_analysis.flow`

GA + dynamical systems unified analysis Import: import "stdlib/dynamics/ga_analysis.flow"

*No `export` items found (internal / extern-only module).*

### `dynamics/gramian.flow`

Controllability / observability Gramians (finite & infinite horizon) Import: import "stdlib/dynamics/gramian.flow"

*No `export` items found (internal / extern-only module).*

### `dynamics/linalg.flow`

Dynamics linear algebra (f64, caller-provided buffers) Import: import "stdlib/dynamics/linalg.flow"

*No `export` items found (internal / extern-only module).*

### `dynamics/lqr.flow`

Discrete LQR helpers (pattern-adoption #162). Scalar-input (m=1) discrete Riccati fixed-point for n <= 8. Prefer this over private mini-linalg in apps until LAPACK DARE lands.

**Functions:**

| Name | Signature | Docs |
|------|-----------|------|
| `dlqr_diag_q_scalar_u` | `(
    ad: ptr<f64>,
    bd: ptr<f64>,
    q_diag: ptr<f64>,
    r: f64,
    n: i32,
    k_out: ptr<f64>,
    max_iter: i32
) -> i32` | Discrete LQR for Ad (n×n), Bd (n×1), diagonal Q, scalar R. Writes gain row K into k_out (length n); control law u = -K x. Returns iteration count on success, or -1 if n out of range / no converge. |
| `lqr_diag_q` | `(ad: ptr<f64>, bd: ptr<f64>, q_diag: ptr<f64>, r: f64,
                           n: i32, k_out: ptr<f64>, max_iter: i32) -> i32` | Alias matching pattern-adoption sketch naming. |

### `dynamics/pde.flow`

PDE helpers (pattern-adoption #163). Stdlib MVP for field evolution without `field` / `boundary` grammar yet. Import: import "stdlib/dynamics/pde.flow"

**Functions:**

| Name | Signature | Docs |
|------|-----------|------|
| `laplacian_1d_at` | `(u: ptr<f64>, i: i32, dx: f64) -> f64` | Second difference at interior index i: (u[i-1] - 2 u[i] + u[i+1]) / dx^2. Caller must ensure 0 < i < n-1. |
| `laplacian_1d` | `(u: ptr<f64>, out: ptr<f64>, n: i32, dx: f64) -> void` | Write laplacian into out for interior cells; out[0] and out[n-1] set to 0. |
| `heat_euler_step_1d` | `(
    u: ptr<f64>,
    next: ptr<f64>,
    n: i32,
    r: f64,
    left_bc: f64,
    right_bc: f64
) -> void` | One explicit Euler heat step with Dirichlet ends: next[i] = u[i] + r * (u[i-1] - 2 u[i] + u[i+1])   for interior next[0] = left_bc, next[n-1] = right_bc where r = alpha * dt / dx^2 (stable for r <= 0.5 on a unit grid). |
| `field_copy_1d` | `(src: ptr<f64>, dst: ptr<f64>, n: i32) -> void` | Copy n samples from src into dst. |

### `dynamics/portrait.flow`

Phase-portrait trail helpers (pattern-adoption #165). Ring-buffer + project helpers until `represent phase_portrait` lowers. Import: import "stdlib/dynamics/portrait.flow"

**Functions:**

| Name | Signature | Docs |
|------|-----------|------|
| `trail_push_2d` | `(
    xs: ptr<f64>,
    zs: ptr<f64>,
    capacity: i32,
    head: ptr<i32>,
    count: ptr<i32>,
    x: f64,
    z: f64
) -> void` | Push (x, z) into a fixed-capacity ring. Updates head/count in place via ptrs. xs/zs must each have length >= capacity. |
| `trail_index` | `(head: i32, count: i32, capacity: i32, i: i32) -> i32` | Oldest→newest index for draw order: i in 0..count maps to ring slot. |
| `project_axis` | `(v: f64, vmin: f64, vmax: f64, width: i32, pad: i32) -> i32` | Linear map from world v in [vmin, xmax] to pixel in [pad, width-pad). vmin>vmax is allowed (inverted axis, e.g. screen y). |

### `dynamics/schur_lattice.flow`

Schur / lattice / orthogonal-colligation route for all-pass synthesis Import: import "stdlib/dynamics/schur_lattice.flow"

*No `export` items found (internal / extern-only module).*

### `dynamics/state_space.flow`

State-space simulation, controllability, transformations Import: import "stdlib/dynamics/state_space.flow"

**Functions:**

| Name | Signature | Docs |
|------|-----------|------|
| `state_step` | `(sys: DynamicalSystem, x: ptr<f64>, u: ptr<f64>, x_next: ptr<f64>) -> void` | One discrete step: x_next = A x + B u. |
| `plant_step` | `(sys: DynamicalSystem, x: ptr<f64>, u: ptr<f64>, x_next: ptr<f64>) -> void` | Alias matching pattern-adoption naming (`plant.step` surface). |

### `dynamics/wfc.flow`

Wave Function Collapse (constraint propagation on tile grids) Import: import "stdlib/dynamics/wfc.flow"

*No `export` items found (internal / extern-only module).*

### `dynamics/wfc_ga_coupling.flow`

GA + WFC coupled guidance for state-space evolution Import: import "stdlib/dynamics/wfc_ga_coupling.flow"

*No `export` items found (internal / extern-only module).*

### `dynamics.flow`

Flow Dynamical Systems Standard Library  Declarative DSL via structs (no new keywords required):

*No `export` items found (internal / extern-only module).*

### `font.flow`

Bitmap font: 5x7 glyphs for printable ASCII (32..126).  Renderer-agnostic on purpose. This module only answers "which pixels are lit

**Functions:**

| Name | Signature | Docs |
|------|-----------|------|
| `font_char_width` | `() -> i32` | — |
| `font_char_height` | `() -> i32` | — |
| `font_glyph_row` | `(ch: i32, row: i32) -> u8` | Row bit pattern for `ch` at `row` (0..6). Unknown characters render blank. |
| `font_pixel` | `(ch: i32, col: i32, row: i32) -> bool` | True when the glyph for `ch` lights the pixel at (col, row). |
| `font_text_width` | `(s: string, scale: i32) -> i32` | Width in pixels of `s` drawn at `scale`, including one blank column between characters (no trailing gap). |
| `font_text_height` | `(scale: i32) -> i32` | — |
| `font_int_width` | `(n: i32, scale: i32) -> i32` | Digits needed to render `n` (a lone minus sign counts as one). |

### `gfx.flow`

gfx: explicit native graphics API (macOS / Linux SDL2 / Windows)  Backend: runtime/gfx_macos.m, runtime/gfx_linux.c, runtime/gfx_windows.c

**Functions:**

| Name | Signature | Docs |
|------|-----------|------|
| `gfx_open` | `(w: i32, h: i32, title: string) -> Gfx` | — |
| `gfx_close` | `(g: Gfx) -> void` | — |
| `gfx_poll` | `(g: Gfx) -> void` | — |
| `gfx_should_close` | `(g: Gfx) -> bool` | — |
| `gfx_key_down` | `(g: Gfx, keycode: i32) -> bool` | — |
| `gfx_clear` | `(g: Gfx, r: i32, g2: i32, b: i32) -> void` | — |
| `gfx_fill_rect` | `(g: Gfx, x: i32, y: i32, w: i32, h: i32, r: i32, g2: i32, b: i32) -> void` | — |
| `gfx_present` | `(g: Gfx) -> void` | — |
| `gfx_frame_pump` | `(g: Gfx) -> bool` | Poll events; return false if the window should close or Esc is down. |
| `gfx_run` | `(g: Gfx, max_frames: i32) -> i32` | Run up to max_frames, calling user-defined flow_gfx_frame(ctx, frame) each tick. Returns the number of frames completed. Requires linking the gfx runtime. |

### `gif.flow`

GIF89a animated encoder, pure Flow. Writes an infinite-loop animation with a fixed 256-color global palette and correct GIF-variant LZW compression. Only libc file I/O and malloc/free cross the FFI line.

**Functions:**

| Name | Signature | Docs |
|------|-----------|------|
| `gif_map_rgb` | `(r: i32, g: i32, b: i32) -> i32` | Nearest palette index for a 24-bit color, integer math only: quantize to the cube, then let one of the 4 grays win when it is strictly closer. |
| `gif_begin` | `(path: string, width: i32, height: i32, delay_cs: i32) -> i32` | Opens `path` and writes the GIF89a header, logical screen descriptor, global color table, and a NETSCAPE2.0 infinite-loop extension. `delay_cs` is the per-frame delay in centiseconds. Returns 0 on success. |
| `gif_add_frame_rgb` | `(pixels: ptr<u8>, width: i32, height: i32) -> i32` | Adds one full frame. `pixels` is RGB24, row-major, width*height*3 bytes. Dimensions must match gif_begin. Returns 0 on success. |
| `gif_end` | `() -> i32` | Writes the trailer and closes the file. Returns 0 on success. |

### `gpu_gradients.flow`

GPU gradient kernels (manual reverse-mode building blocks)  These are elementwise backward kernels for ML training on GPU, not a

*No `export` items found (internal / extern-only module).*

### `gpu_kernels.flow`

GPU kernels for ML workloads (Metal/CUDA codegen via @gpu) Mojo-style: annotate kernels, compile with `flow gpu <file>`

*No `export` items found (internal / extern-only module).*

### `gpu_memory.flow`

First-class GPU / unified memory  CPU heap stays in stdlib/memory.flow.

**Structs:** `GpuBuffer`

**Constants:**

- `GPU_MEM_DEFAULT: i32`
- `GPU_MEM_SHARED: i32`
- `GPU_MEM_PRIVATE: i32`

**Functions:**

| Name | Signature | Docs |
|------|-----------|------|
| `gpu_available` | `() -> bool` | — |
| `gpu_backend_name` | `() -> string` | — |
| `gpu_null_buffer` | `() -> GpuBuffer` | — |
| `gpu_is_null` | `(buf: GpuBuffer) -> bool` | — |
| `gpu_alloc_flags` | `(size: i64, flags: i32) -> GpuBuffer` | — |
| `gpu_alloc` | `(size: i64) -> GpuBuffer` | Default = unified/shared on Metal |
| `gpu_alloc_unified` | `(size: i64) -> GpuBuffer` | — |
| `gpu_alloc_private` | `(size: i64) -> GpuBuffer` | — |
| `gpu_alloc_f32` | `(count: i64) -> GpuBuffer` | — |
| `gpu_alloc_f64` | `(count: i64) -> GpuBuffer` | — |
| `gpu_alloc_i32` | `(count: i64) -> GpuBuffer` | — |
| `gpu_free` | `(buf: GpuBuffer) -> void` | — |
| `gpu_size` | `(buf: GpuBuffer) -> i64` | — |
| `gpu_host_ptr` | `(buf: GpuBuffer) -> ptr<void>` | Host mapping for unified/shared buffers (null if private) |
| `gpu_is_unified` | `(buf: GpuBuffer) -> bool` | — |
| `gpu_copy_h2d` | `(dst: GpuBuffer, src: ptr<void>, nbytes: i64) -> i32` | — |
| `gpu_copy_d2h` | `(dst: ptr<void>, src: GpuBuffer, nbytes: i64) -> i32` | — |
| `gpu_copy_h2d_i32` | `(dst: GpuBuffer, src: ptr<i32>, nbytes: i64) -> i32` | Typed convenience overloads (ptr<i32>/f32/f64 decay to void* at the ABI) |
| `gpu_copy_d2h_i32` | `(dst: ptr<i32>, src: GpuBuffer, nbytes: i64) -> i32` | — |
| `gpu_copy_h2d_f32` | `(dst: GpuBuffer, src: ptr<f32>, nbytes: i64) -> i32` | — |
| `gpu_copy_d2h_f32` | `(dst: ptr<f32>, src: GpuBuffer, nbytes: i64) -> i32` | — |
| `gpu_copy_d2d` | `(dst: GpuBuffer, src: GpuBuffer, nbytes: i64) -> i32` | — |
| `gpu_sync` | `() -> void` | — |
| `gpu_allocate` | `(size: i64) -> GpuBuffer` | Aliases matching docs/library/core.md naming |
| `gpu_copy_to_device` | `(dst: GpuBuffer, src: ptr<void>, nbytes: i64) -> i32` | — |
| `gpu_copy_from_device` | `(dst: ptr<void>, src: GpuBuffer, nbytes: i64) -> i32` | — |
| `gpu_copy_device_to_device` | `(dst: GpuBuffer, src: GpuBuffer, nbytes: i64) -> i32` | — |
| `unified_allocate` | `(size: i64) -> GpuBuffer` | — |

### `gpu_sim.flow`

GPU simulation layer (CPU-backed) to model DeviceContext/Queue/Buffer/Layouts. This is a compatibility + teaching layer to mirror Mojo-style APIs.

*No `export` items found (internal / extern-only module).*

### `io.flow`

**Functions:**

| Name | Signature | Docs |
|------|-----------|------|
| `print_benchmark` | `(name: string, time: f64) -> void` | — |

### `logpkg.flow`

Minimal logging package for tests/examples.

*No `export` items found (internal / extern-only module).*

### `math.flow`

Math Module - Exported functions and constants This module demonstrates FLOW's export system

**Constants:**

- `PI: f32`
- `E: f32`
- `GOLDEN_RATIO: f32`

**Functions:**

| Name | Signature | Docs |
|------|-----------|------|
| `add` | `(a: f32, b: f32) -> f32` | Add two f32 values: a + b. |
| `subtract` | `(a: f32, b: f32) -> f32` | Subtract two f32 values: a - b. |
| `multiply` | `(a: f32, b: f32) -> f32` | Multiply two f32 values: a * b. |
| `divide` | `(a: f32, b: f32) -> f32` | Divide a by b; returns 0 and prints on division by zero. |
| `power` | `(base: f32, exponent: f32) -> f32` | Integer-power via repeated multiply; supports negative exponents as reciprocal. Exponent is treated as a whole number (loop count), not a general real power. |
| `sin` | `(x: f32) -> f32` | Sine of x (radians). Intrinsic in MLIR; stub returns 0 in C fallback. |
| `cos` | `(x: f32) -> f32` | Cosine of x (radians). Intrinsic in MLIR; stub returns 0 in C fallback. |
| `sqrt` | `(x: f32) -> f32` | Square root of x. Intrinsic in MLIR; stub returns 0 in C fallback. Domain: x >= 0 for real results. |
| `fabs` | `(x: f32) -> f32` | Absolute value of x (fabs intrinsic in MLIR; stub returns 0 in C fallback). |
| `abs` | `(x: f32) -> f32` | Absolute value of x: \|x\|. |
| `tan` | `(x: f32) -> f32` | Tangent of x (radians): sin(x)/cos(x). Returns 0 if cos(x) == 0. |
| `log` | `(x: f32) -> f32` | Natural logarithm ln(x) via Newton's method. Domain: x > 0; returns 0 and prints for non-positive input. |
| `exp` | `(x: f32) -> f32` | Exponential e^x via Taylor series (20 terms). |
| `fibonacci` | `(n: i32) -> i32` | nth Fibonacci number (F(0)=0, F(1)=1); returns 0 for n <= 0. |
| `gcd` | `(a: i32, b: i32) -> i32` | Greatest common divisor of a and b (Euclidean algorithm). |
| `lcm` | `(a: i32, b: i32) -> i32` | Least common multiple of a and b: \|a*b\|/gcd(a,b). |
| `is_prime` | `(n: i32) -> bool` | True if n is prime; false for n <= 1. Trial division up to sqrt(n). |
| `factorial_big` | `(n: i32) -> i64` | Factorial n! as i64; returns 1 for n <= 1. Watch for overflow on large n. |

### `memory.flow`

Manual memory management — real libc heap (C backend)  Flow has no GC. Heap memory is yours to allocate and free.

**Structs:** `Arena`

**Functions:**

| Name | Signature | Docs |
|------|-----------|------|
| `sizeof_i8` | `() -> i64` | ── Sizes ────────────────────────────────────────────────────────── |
| `sizeof_i32` | `() -> i64` | — |
| `sizeof_i64` | `() -> i64` | — |
| `sizeof_f32` | `() -> i64` | — |
| `sizeof_f64` | `() -> i64` | — |
| `sizeof_ptr` | `() -> i64` | — |
| `alignof_i32` | `() -> i64` | — |
| `alignof_i64` | `() -> i64` | — |
| `alignof_f32` | `() -> i64` | — |
| `alignof_f64` | `() -> i64` | — |
| `is_power_of_two` | `(value: i64) -> bool` | ── Alignment helpers ─────────────────────────────────────────────── |
| `align_up` | `(size: i64, alignment: i64) -> i64` | — |
| `align_down` | `(size: i64, alignment: i64) -> i64` | — |
| `alloc_bytes` | `(size: i64) -> ptr<void>` | ── Typed heap helpers ────────────────────────────────────────────── |
| `alloc_zeroed` | `(size: i64) -> ptr<void>` | — |
| `alloc_i32` | `(count: i64) -> ptr<i32>` | — |
| `alloc_f32` | `(count: i64) -> ptr<f32>` | — |
| `alloc_f64` | `(count: i64) -> ptr<f64>` | — |
| `memory_zero_i32` | `(p: ptr<i32>, count: i64) -> void` | — |
| `memory_copy_i32` | `(dst: ptr<i32>, src: ptr<i32>, count: i64) -> void` | — |
| `arena_create` | `(capacity: i64) -> Arena` | — |
| `arena_alloc` | `(arena: ptr<Arena>, size: i64) -> ptr<void>` | — |
| `arena_alloc_i32` | `(arena: ptr<Arena>, count: i64) -> ptr<i32>` | — |
| `arena_alloc_f32` | `(arena: ptr<Arena>, count: i64) -> ptr<f32>` | — |
| `arena_reset` | `(arena: ptr<Arena>) -> void` | — |
| `arena_destroy` | `(arena: ptr<Arena>) -> void` | — |
| `arena_used` | `(arena: Arena) -> i64` | — |
| `arena_remaining` | `(arena: Arena) -> i64` | — |

### `memory_simple.flow`

Memory Management Module Provides low-level memory allocation, manipulation, and safety functions

**Structs:** `MemoryPool`

**Functions:**

| Name | Signature | Docs |
|------|-----------|------|
| `malloc` | `(size: i32) -> i32` | Memory allocation functions |
| `calloc` | `(nmemb: i32, size: i32) -> i32` | — |
| `realloc` | `(ptr: i32, size: i32) -> i32` | — |
| `free` | `(ptr: i32) -> void` | — |
| `aligned_alloc` | `(alignment: i32, size: i32) -> i32` | — |
| `memcpy` | `(dest: i32, src: i32, n: i32) -> i32` | Memory manipulation functions |
| `memmove` | `(dest: i32, src: i32, n: i32) -> i32` | — |
| `memset` | `(dest: i32, c: i32, n: i32) -> i32` | — |
| `memcmp` | `(s1: i32, s2: i32, n: i32) -> i32` | — |
| `is_power_of_two` | `(value: i32) -> bool` | Memory alignment and layout functions |
| `alignof_i32` | `() -> i32` | — |
| `alignof_f32` | `() -> i32` | — |
| `alignof_i8` | `() -> i32` | — |
| `sizeof_i32` | `() -> i32` | — |
| `sizeof_f32` | `() -> i32` | — |
| `sizeof_i8` | `() -> i32` | — |
| `offset_of_Point` | `(field: string) -> i32` | — |
| `is_aligned` | `(ptr: i32, alignment: i32) -> bool` | — |
| `align_up` | `(size: i32, alignment: i32) -> i32` | — |
| `align_down` | `(size: i32, alignment: i32) -> i32` | — |
| `memory_check` | `(ptr: i32, size: i32) -> bool` | Memory safety and debugging functions |
| `memory_check_write` | `(ptr: i32, size: i32) -> bool` | — |
| `memory_fill_pattern` | `(ptr: i32, pattern: i32, count: i32) -> void` | — |
| `memory_zero` | `(ptr: i32, size: i32) -> void` | — |
| `memory_copy_nonoverlapping` | `(dest: i32, src: i32, n: i32) -> void` | — |
| `memory_copy_overlapping` | `(dest: i32, src: i32, n: i32) -> void` | — |
| `alloca` | `(size: i32) -> i32` | Stack allocation functions |
| `stack_array_i32` | `(count: i32) -> i32` | — |
| `stack_array_f32` | `(count: i32) -> i32` | — |
| `memory_pool_create` | `(size: i32) -> MemoryPool` | — |
| `memory_pool_alloc` | `(pool: MemoryPool, size: i32, alignment: i32) -> i32` | — |
| `memory_pool_reset` | `(pool: MemoryPool) -> void` | — |
| `memory_pool_destroy` | `(pool: MemoryPool) -> void` | — |
| `memory_dump` | `(ptr: i32, size: i32, bytes_per_line: i32) -> void` | Memory debugging utilities |
| `memory_validate` | `(ptr: i32, size: i32) -> bool` | — |
| `format_hex` | `(value: i32) -> string` | Helper functions |
| `format_hex_ptr` | `(ptr: i32) -> string` | — |

### `memory_working.flow`

Simple Memory Management Module Basic memory allocation and manipulation functions

**Structs:** `MemoryPool`

**Functions:**

| Name | Signature | Docs |
|------|-----------|------|
| `malloc` | `(size: i32) -> i32` | Memory allocation functions |
| `calloc` | `(nmemb: i32, size: i32) -> i32` | — |
| `realloc` | `(ptr: i32, size: i32) -> i32` | — |
| `free` | `(ptr: i32) -> i32` | — |
| `aligned_alloc` | `(alignment: i32, size: i32) -> i32` | — |
| `memcpy` | `(dest: i32, src: i32, n: i32) -> i32` | Memory manipulation functions |
| `memmove` | `(dest: i32, src: i32, n: i32) -> i32` | — |
| `memset` | `(dest: i32, c: i32, n: i32) -> i32` | — |
| `memcmp` | `(s1: i32, s2: i32, n: i32) -> i32` | — |
| `is_power_of_two` | `(value: i32) -> bool` | Memory alignment and layout functions |
| `alignof_i32` | `() -> i32` | — |
| `alignof_f32` | `() -> i32` | — |
| `alignof_i8` | `() -> i32` | — |
| `sizeof_i32` | `() -> i32` | — |
| `sizeof_f32` | `() -> i32` | — |
| `sizeof_i8` | `() -> i32` | — |
| `offset_of_Point` | `(field: string) -> i32` | — |
| `is_aligned` | `(ptr: i32, alignment: i32) -> bool` | — |
| `align_up` | `(size: i32, alignment: i32) -> i32` | — |
| `align_down` | `(size: i32, alignment: i32) -> i32` | — |
| `memory_check` | `(ptr: i32, size: i32) -> bool` | Memory safety and debugging functions |
| `memory_check_write` | `(ptr: i32, size: i32) -> bool` | — |
| `memory_fill_pattern` | `(ptr: i32, pattern: i32, count: i32) -> i32` | — |
| `memory_zero` | `(ptr: i32, size: i32) -> i32` | — |
| `memory_copy_nonoverlapping` | `(dest: i32, src: i32, n: i32) -> i32` | — |
| `memory_copy_overlapping` | `(dest: i32, src: i32, n: i32) -> i32` | — |
| `alloca` | `(size: i32) -> i32` | Stack allocation functions |
| `stack_array_i32` | `(count: i32) -> i32` | — |
| `stack_array_f32` | `(count: i32) -> i32` | — |
| `memory_pool_create` | `(size: i32) -> MemoryPool` | — |
| `memory_pool_alloc` | `(pool: MemoryPool, size: i32, alignment: i32) -> i32` | — |
| `memory_pool_reset` | `(pool: MemoryPool) -> i32` | — |
| `memory_pool_destroy` | `(pool: MemoryPool) -> i32` | — |
| `memory_dump` | `(ptr: i32, size: i32, bytes_per_line: i32) -> i32` | Memory debugging utilities |
| `memory_validate` | `(ptr: i32, size: i32) -> bool` | — |
| `format_hex` | `(value: i32) -> string` | Helper functions |
| `format_hex_ptr` | `(ptr: i32) -> string` | — |

### `ml_nn.flow`

ML neural-network building blocks (stdlib) Import: import "stdlib/ml_nn.flow" MLIR-first training via tensor ops + ptr-based SGD

*No `export` items found (internal / extern-only module).*

### `ml_opt.flow`

ML optimizers (stdlib) Import: import "stdlib/ml_opt.flow"

*No `export` items found (internal / extern-only module).*

### `net.flow`

FLOW Networking Standard Library TCP/UDP sockets, HTTP client

*No `export` items found (internal / extern-only module).*

### `nn.flow`

Minimal Neural Network utilities (stdlib)  Purpose: reusable training/prediction for tiny MLPs with explicit backprop.

**Structs:** `Net2x2x1`, `Grads2x2x1`, `Net2x4x1`, `Grads2x4x1`, `Net2x8x1`, `Grads2x8x1`

**Functions:**

| Name | Signature | Docs |
|------|-----------|------|
| `net2x2x1_param_get` | `(net: Net2x2x1, idx: i32) -> f32` | — |
| `net2x2x1_param_set` | `(net: Net2x2x1, idx: i32, value: f32) -> Net2x2x1` | — |
| `net2x2x1_grad_get` | `(g: Grads2x2x1, idx: i32) -> f32` | — |
| `net2x2x1_predict` | `(net: Net2x2x1, x0: f32, x1: f32) -> f32` | — |
| `net2x2x1_loss_xor` | `(net: Net2x2x1) -> f32` | — |
| `net2x2x1_grads_xor` | `(net: Net2x2x1) -> Grads2x2x1` | — |
| `net2x2x1_step` | `(net: Net2x2x1, grads: Grads2x2x1, lr: f32) -> Net2x2x1` | — |
| `net2x2x1_gradcheck_xor` | `(net: Net2x2x1, eps: f32) -> f32` | — |
| `net2x4x1_predict` | `(net: Net2x4x1, x0: f32, x1: f32) -> f32` | — |
| `net2x4x1_loss_xor` | `(net: Net2x4x1) -> f32` | — |
| `net2x4x1_grads_xor` | `(net: Net2x4x1) -> Grads2x4x1` | — |
| `net2x4x1_step` | `(net: Net2x4x1, grads: Grads2x4x1, lr: f32) -> Net2x4x1` | — |
| `net2x8x1_predict` | `(net: Net2x8x1, x0: f32, x1: f32) -> f32` | — |
| `net2x8x1_loss_xor` | `(net: Net2x8x1) -> f32` | — |
| `net2x8x1_grads_xor` | `(net: Net2x8x1) -> Grads2x8x1` | — |
| `net2x8x1_step` | `(net: Net2x8x1, grads: Grads2x8x1, lr: f32) -> Net2x8x1` | — |

### `nn_autogen.flow`

Auto-generated backprop for XOR loss (2x2x1) via scripts/tools/grad/flow_grad_flow.py  This file demonstrates "no hand-written backprop": gradients are generated from

**Functions:**

| Name | Signature | Docs |
|------|-----------|------|
| `net2x2x1_grads_xor_autogen` | `(net: Net2x2x1) -> Grads2x2x1` | Convert Grad_xor_loss_clean (generated) to Grads2x2x1 (stdlib shape) |

### `nn_xor_loss_clean.flow`

XOR loss with helper functions (for cleaner gradient codegen demo)  This version uses multi-arg helper functions instead of inlining everything.

*No `export` items found (internal / extern-only module).*

### `nn_xor_loss_clean_grad.flow`

*No `export` items found (internal / extern-only module).*

### `nn_xor_loss_params.flow`

Input file for codegen: scalar XOR loss over parameters Constraint: codegen supports only 1-arg calls, so we inline everything.

*No `export` items found (internal / extern-only module).*

### `nn_xor_loss_params_grad.flow`

*No `export` items found (internal / extern-only module).*

### `option.flow`

Option Type Represents an optional value: either Some(value) or None

*No `export` items found (internal / extern-only module).*

### `posix.flow`

FLOW POSIX Standard Library File I/O, processes, environment, and system calls

*No `export` items found (internal / extern-only module).*

### `process.flow`

Process / host-command helpers Runtime: flow_run_cmd / flow_have_cmd in runtime/flow_sys_info.c

**Functions:**

| Name | Signature | Docs |
|------|-----------|------|
| `run_cmd` | `(cmd: string) -> i32` | — |
| `have_cmd` | `(name: string) -> bool` | — |
| `env_is` | `(name: string, want: string) -> bool` | — |
| `str_eq` | `(a: string, b: string) -> bool` | — |

### `python_embed.flow`

Minimal Python embedding interface (extern-backed)

**Structs:** `PythonContext`

**Constants:**

- `PY_OK: i32`
- `PY_ERR_INIT: i32`
- `PY_ERR_PATH: i32`
- `PY_ERR_IMPORT: i32`
- `PY_ERR_CALL: i32`

**Functions:**

| Name | Signature | Docs |
|------|-----------|------|
| `python_init_or_print` | `() -> bool` | — |
| `python_add_paths` | `(p1: string, p2: string) -> i32` | — |
| `python_import_or_null` | `(name: string) -> ptr<void>` | — |
| `python_call0_or_print` | `(py_mod: ptr<void>, fn_name: string) -> i32` | — |
| `python_call1_str_or_print` | `(py_mod: ptr<void>, fn_name: string, arg: string) -> i32` | — |
| `python_call1_i32_or_print` | `(py_mod: ptr<void>, fn_name: string, arg: i32) -> i32` | — |
| `python_call1_f32_or_print` | `(py_mod: ptr<void>, fn_name: string, arg: f32) -> i32` | — |
| `python_call1_bool_or_print` | `(py_mod: ptr<void>, fn_name: string, arg: bool) -> i32` | — |
| `python_begin` | `(p1: string, p2: string) -> PythonContext` | — |
| `python_import` | `(ctx: PythonContext, name: string) -> PythonContext` | — |
| `python_call` | `(ctx: PythonContext, fn_name: string) -> PythonContext` | — |
| `python_call_str` | `(ctx: PythonContext, fn_name: string, arg: string) -> PythonContext` | — |
| `python_call_i32` | `(ctx: PythonContext, fn_name: string, arg: i32) -> PythonContext` | — |
| `python_call_f32` | `(ctx: PythonContext, fn_name: string, arg: f32) -> PythonContext` | — |
| `python_call_bool` | `(ctx: PythonContext, fn_name: string, arg: bool) -> PythonContext` | — |
| `python_end` | `() -> void` | — |

### `result.flow`

Result Type Represents either success (Ok(value)) or failure (Err(error))

*No `export` items found (internal / extern-only module).*

### `sdl2.flow`

SDL2 bindings (minimal)  This is a deliberately tiny subset needed for simple 2D apps.

*No `export` items found (internal / extern-only module).*

### `slice.flow`

FLOW Slice Type A slice is a view into a contiguous block of memory (ptr + length)

*No `export` items found (internal / extern-only module).*

### `srir.flow`

**Functions:**

| Name | Signature | Docs |
|------|-----------|------|
| `rect` | `(x: f32, y: f32, w: f32, h: f32, r: i32, g: i32, b: i32, a: i32) -> void` | — |
| `circle` | `(x: f32, y: f32, radius: f32, r: i32, g: i32, b: i32, a: i32) -> void` | — |
| `group` | `() -> void` | — |
| `end_group` | `() -> void` | — |
| `transform` | `(tx: f32, ty: f32, sx: f32, sy: f32, rot: f32) -> void` | — |
| `end_transform` | `() -> void` | — |
| `render` | `(filename: string, width: i32, height: i32) -> void` | — |

### `string.flow`

FLOW String Utilities

*No `export` items found (internal / extern-only module).*

### `sys_info.flow`

System information helpers (extern-backed)

**Functions:**

| Name | Signature | Docs |
|------|-----------|------|
| `os_name` | `() -> string` | — |
| `cpu_name` | `() -> string` | — |
| `cpu_arch` | `() -> string` | — |
| `cpu_cores` | `() -> i32` | — |
| `cpu_features_string` | `() -> string` | — |

### `tensor.flow`

Tensor: N-dimensional array type for neural networks (stdlib) Import: import "stdlib/tensor.flow" MLIR-first ML workloads: use with `flow ml` or `flow mlir-run`

*No `export` items found (internal / extern-only module).*

### `text.flow`

Text drawing for the gfx backends: blits stdlib/font.flow glyphs as rects.  Games used to hand-roll seven-segment digits out of rectangles. This draws

**Functions:**

| Name | Signature | Docs |
|------|-----------|------|
| `gfx_draw_char` | `(g: Gfx, x: i32, y: i32, ch: i32, scale: i32,
                              r: i32, gr: i32, b: i32) -> i32` | One character. Returns the x advance so callers can chain. |
| `gfx_draw_text` | `(g: Gfx, x: i32, y: i32, s: string, scale: i32,
                              r: i32, gr: i32, b: i32) -> i32` | — |
| `gfx_draw_text_centered` | `(g: Gfx, cx: i32, y: i32, s: string, scale: i32,
                                       r: i32, gr: i32, b: i32) -> i32` | Centered on `cx`. |
| `gfx_draw_text_right` | `(g: Gfx, rx: i32, y: i32, s: string, scale: i32,
                                    r: i32, gr: i32, b: i32) -> i32` | Right edge at `rx`. |
| `gfx_draw_int` | `(g: Gfx, x: i32, y: i32, n: i32, scale: i32,
                             r: i32, gr: i32, b: i32) -> i32` | Integers without going through string formatting: draw digits directly so callers need no scratch buffer. |
| `gfx_draw_int_right` | `(g: Gfx, rx: i32, y: i32, n: i32, scale: i32,
                                   r: i32, gr: i32, b: i32) -> i32` | — |
| `gfx_draw_int_padded` | `(g: Gfx, x: i32, y: i32, n: i32, width: i32, scale: i32,
                                    r: i32, gr: i32, b: i32) -> i32` | Zero-padded to `width` digits (clock and score displays). |
| `gfx_draw_fixed` | `(g: Gfx, x: i32, y: i32, value: f64, decimals: i32, scale: i32,
                               r: i32, gr: i32, b: i32) -> i32` | Fixed-point float with `decimals` places (no printf, no allocation). |

### `time.flow`

**Functions:**

| Name | Signature | Docs |
|------|-----------|------|
| `get_time` | `() -> f64` | — |

### `ui.flow`

FLOW Terminal UI Helpers  Minimal, dependency-free helpers for building text UIs.

**Functions:**

| Name | Signature | Docs |
|------|-----------|------|
| `ui_clear` | `() -> void` | ANSI escape helpers --------------------------------------------------------- |
| `ui_hide_cursor` | `() -> void` | — |
| `ui_show_cursor` | `() -> void` | — |
| `ui_reset_style` | `() -> void` | — |
| `ui_bold_on` | `() -> void` | — |
| `ui_dim_on` | `() -> void` | — |
| `ui_fg` | `(code: i32) -> void` | — |
| `ui_bg` | `(code: i32) -> void` | — |
| `ui_newline` | `() -> void` | — |
| `ui_flush` | `() -> void` | — |
| `ui_print_spaces` | `(n: i32) -> void` | — |
| `ui_read_char` | `() -> i32` | Input helpers --------------------------------------------------------------- |
| `ui_read_non_newline_char` | `() -> i32` | — |
| `ui_consume_line` | `() -> void` | — |

### `ui2d.flow`

UI2D: tiny immediate-mode 2D drawing on SDL2  This is “graphics library written in FLOW”: rectangles + a built-in bitmap

**Functions:**

| Name | Signature | Docs |
|------|-----------|------|
| `ui2d_init` | `(title: string, w: i32, h: i32) -> Ui2D` | — |
| `ui2d_shutdown` | `(ui: Ui2D) -> void` | — |
| `ui2d_poll` | `(ui: Ui2D) -> Ui2D` | — |
| `ui2d_key_down` | `(scancode: i32) -> bool` | — |
| `ui2d_begin` | `(ui: Ui2D, clear: Color) -> void` | — |
| `ui2d_end` | `(ui: Ui2D) -> void` | — |
| `ui2d_fill_rect` | `(ui: Ui2D, x: i32, y: i32, w: i32, h: i32, c: Color) -> void` | — |
| `ui2d_draw_digit` | `(ui: Ui2D, x: i32, y: i32, d: i32, scale: i32, c: Color) -> void` | — |
| `ui2d_draw_number` | `(ui: Ui2D, x: i32, y: i32, n: i32, scale: i32, c: Color) -> void` | — |

### `ui_layout.flow`

Simple UI layout helpers for DSL blocks

**Structs:** `UiRect`, `UiLayoutFrame`, `UiLayoutState`

**Constants:**

- `UI_JUSTIFY_START: i32`
- `UI_JUSTIFY_CENTER: i32`
- `UI_JUSTIFY_END: i32`

**Functions:**

| Name | Signature | Docs |
|------|-----------|------|
| `ui_layout_set_view` | `(state: ptr<UiLayoutState>, win_w: f32, win_h: f32) -> void` | — |
| `ui_next_rect` | `(state: ptr<UiLayoutState>) -> UiRect` | — |
| `ui_layout_begin` | `(state: ptr<UiLayoutState>, cols: i32, rows: i32, pad: i32) -> void` | — |
| `ui_layout_end` | `(state: ptr<UiLayoutState>) -> void` | — |
| `ui_row_begin` | `(state: ptr<UiLayoutState>, cols: i32, gap: i32, pad: i32, justify: i32) -> void` | — |
| `ui_row_end` | `(state: ptr<UiLayoutState>) -> void` | — |
| `ui_column_begin` | `(state: ptr<UiLayoutState>, rows: i32, gap: i32, pad: i32, justify: i32) -> void` | — |
| `ui_column_end` | `(state: ptr<UiLayoutState>) -> void` | — |
| `ui_grid_begin` | `(state: ptr<UiLayoutState>, cols: i32, rows: i32, gap: i32, pad: i32, justify_x: i32, justify_y: i32) -> void` | — |
| `ui_grid_end` | `(state: ptr<UiLayoutState>) -> void` | — |
| `ui_stack_begin` | `(state: ptr<UiLayoutState>) -> void` | — |
| `ui_stack_end` | `(state: ptr<UiLayoutState>) -> void` | — |
| `ui_box` | `(state: ptr<UiLayoutState>) -> UiRect` | — |

### `vec.flow`

Flow Standard Library: Vector Types Built-in Vec2/Vec3 with operator overloading

*No `export` items found (internal / extern-only module).*

### `vulkan.flow`

Vulkan Flow wrapper (macOS + MoltenVK demo bridge)

**Functions:**

| Name | Signature | Docs |
|------|-----------|------|
| `vulkan_run_basic` | `(opts: VulkanOptions) -> i32` | — |
| `vulkan_run_advanced` | `(opts: VulkanOptions) -> i32` | — |
| `vulkan_run_basic_with_config` | `(opts: VulkanOptions, cfg: VulkanConfig) -> i32` | — |
| `vulkan_run_advanced_with_config` | `(opts: VulkanOptions, cfg: VulkanConfig) -> i32` | — |

### `vulkan_abi_renderer.flow`

**Functions:**

| Name | Signature | Docs |
|------|-----------|------|
| `abi_renderer_init` | `() -> AbiRenderer` | — |
| `abi_renderer_begin_frame` | `(r: AbiRenderer) -> i32` | — |
| `abi_renderer_end_frame` | `(r: AbiRenderer) -> void` | — |
| `abi_renderer_create_instance_buffer` | `(r: AbiRenderer, capacity: i32) -> i32` | — |
| `abi_renderer_update_instance_buffer` | `(r: AbiRenderer, buf: i32, instance_data: ptr<f32>, count: i32) -> void` | — |
| `abi_renderer_draw_instance_buffer` | `(r: AbiRenderer, buf: i32, count: i32) -> void` | — |
| `abi_renderer_create_texture` | `(r: AbiRenderer, width: i32, height: i32) -> i32` | — |
| `abi_renderer_update_texture` | `(r: AbiRenderer, tex: i32, pixels: ptr<u8>, width: i32, height: i32) -> void` | — |
| `abi_renderer_upload_mesh` | `(r: AbiRenderer, vertices: ptr<f32>, vertex_count: i32, indices: ptr<u16>, index_count: i32) -> void` | — |
| `abi_renderer_set_clear` | `(r: AbiRenderer, r_col: f32, g_col: f32, b_col: f32) -> void` | — |
| `abi_renderer_set_camera` | `(r: AbiRenderer, distance: f32, pitch: f32, yaw: f32) -> void` | — |
| `abi_renderer_set_viewport` | `(r: AbiRenderer, width: i32, height: i32) -> void` | — |
| `abi_renderer_set_window_scale` | `(r: AbiRenderer, scale: f32, force_square: bool) -> void` | — |

### `vulkan_renderer.flow`

**Functions:**

| Name | Signature | Docs |
|------|-----------|------|
| `renderer_basic` | `() -> Renderer` | — |
| `renderer_advanced` | `() -> Renderer` | — |
| `renderer_set_clear` | `(r: Renderer, r_col: f32, g_col: f32, b_col: f32) -> Renderer` | — |
| `renderer_set_window` | `(r: Renderer, w: i32, h: i32, title: string) -> Renderer` | — |
| `renderer_set_texture` | `(r: Renderer, path: string) -> Renderer` | — |
| `renderer_set_texture2` | `(r: Renderer, path: string) -> Renderer` | — |
| `renderer_pick_texture` | `(r: Renderer) -> Renderer` | — |
| `renderer_pick_texture2` | `(r: Renderer) -> Renderer` | — |
| `renderer_set_camera` | `(r: Renderer, distance: f32, pitch: f32, yaw: f32) -> Renderer` | — |
| `renderer_set_camera_speed` | `(r: Renderer, move_speed: f32, mouse_sensitivity: f32) -> Renderer` | — |
| `renderer_set_camera_smoothing` | `(r: Renderer, smoothing: f32) -> Renderer` | — |
| `renderer_set_material1` | `(r: Renderer, r_col: f32, g_col: f32, b_col: f32) -> Renderer` | — |
| `renderer_set_material2` | `(r: Renderer, r_col: f32, g_col: f32, b_col: f32) -> Renderer` | — |
| `renderer_set_instances` | `(r: Renderer, count: i32) -> Renderer` | — |
| `renderer_set_trace` | `(r: Renderer, trace_on: bool) -> Renderer` | — |
| `renderer_set_validation` | `(r: Renderer, validation_on: bool) -> Renderer` | — |
| `renderer_run` | `(r: Renderer) -> i32` | — |

