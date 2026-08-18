# Standard Library API (generated)

> Auto-generated from `lib/stdlib/` on 2026-08-18 by `scripts/gen_stdlib_docs.py`. Per-function docs come from `#` comments immediately above each `export function`.

**111** modules scanned.

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

**Structs:** `Delay`, `Distortion`, `Chorus`, `Compressor`, `Bitcrusher`, `CombFilter`, `AllpassFilter`, `Reverb`

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
| `comb_new` | `(delay_ms: f32, sr: SampleRate) -> CombFilter` | — |
| `comb_tick` | `(comb: CombFilter, input: f32) -> CombFilter` | — |
| `allpass_new` | `(delay_ms: f32, sr: SampleRate) -> AllpassFilter` | — |
| `allpass_tick` | `(allpass: AllpassFilter, input: f32) -> AllpassFilter` | — |
| `reverb_new` | `(room_size: f32, damping: f32, mix: f32) -> Reverb` | — |
| `reverb_small_room` | `() -> Reverb` | Presets |
| `reverb_medium_hall` | `() -> Reverb` | — |
| `reverb_large_hall` | `() -> Reverb` | — |
| `reverb_plate` | `() -> Reverb` | — |
| `reverb_tick` | `(rev: Reverb, input: f32) -> Reverb` | Process one sample, updating the Reverb state and returning the updated Reverb struct |
| `reverb_process` | `(rev: Reverb, input: f32) -> f32` | Process one sample (simplified - full reverb needs comb filters) Note: To use the true stateful comb/allpass reverb, use reverb_tick instead. |

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
| `notation_add` | `(reader: ptr<NotationReader>, midi: i32, duration: i32) -> bool` | Append one note. Returns false when the reader is full. This is how you build a sequence today. The text-file parser below is not implemented; it returns a fixed tune whatever path you give it, and the comment there says so. |
| `notation_add_rest` | `(reader: ptr<NotationReader>, duration: i32) -> bool` | Append a rest. A MIDI number below 0 means silence; players are expected to check for it. |
| `note_is_rest` | `(n: MusicNote) -> bool` | — |
| `notation_clear` | `(reader: ptr<NotationReader>) -> void` | — |
| `notation_total_sixteenths` | `(reader: ptr<NotationReader>) -> i32` | Total length of the sequence in sixteenth notes. |
| `notation_load_file` | `(reader: ptr<NotationReader>, path: string) -> bool` | NOT A PARSER. This ignores `path` entirely and loads a fixed tune, so that the players in examples/audio have something to read while the text format above is still unimplemented. Use notation_add to build a real sequence. |
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
| `sine` | `(phase: f64) -> f32` | Sine wave: sin(2π * phase) Uses libm sinf. The previous 7th-order Taylor series was off by 7.5% at the ends of the cycle (sin(π) came out as -0.075 instead of 0), which is roughly -25 dB of harmonic distortion on every sine in the library. |
| `saw` | `(phase: f64) -> f32` | Saw wave: 2 * phase - 1 (naive, has aliasing at high frequencies) |
| `saw_reverse` | `(phase: f64) -> f32` | Reverse saw (ramp down) |
| `square` | `(phase: f64) -> f32` | Square wave: phase < 0.5 ? 1.0 : -1.0 (naive, has aliasing) |
| `pulse` | `(phase: f64, width: f64) -> f32` | Pulse wave with variable width [0.0, 1.0] |
| `triangle` | `(phase: f64) -> f32` | Triangle wave: 4 * \|phase - 0.5\| - 1 |
| `saw_blep` | `(phase: f64, increment: f64) -> f32` | Band-limited saw using PolyBLEP |
| `square_blep` | `(phase: f64, increment: f64) -> f32` | Band-limited square using PolyBLEP |
| `noise_new` | `(seed: i64) -> NoiseState` | Create noise generator with seed |
| `noise_tick` | `(n: NoiseState) -> NoiseState` | Generate next random sample and update state. The modulus is a mask, not a sign flip. Without it the seed grows without bound (the state is i64, so the multiply just keeps getting bigger) and noise_value returns numbers in the billions rather than in [-1, 1). Any |
| `noise_value` | `(n: NoiseState) -> f32` | Current noise value in [-1.0, 1.0). |
| `white_noise` | `(n: NoiseState) -> f32` | The value of the current state. This does not advance the generator: the state is a value, so the caller has to hold the result of noise_tick. n = noise_tick(n) let x: f32 = white_noise(n) |
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

### `audio/safety.flow`

Audio Safety Module  The master chain every Flow audio example runs through before a sample

**Structs:** `TruePeak`, `Limiter`, `SafetyConfig`, `SafetyChain`

**Constants:**

- `SAFETY_LOOKAHEAD_MAX: i32`
- `SAFETY_DEFAULT_CEILING_DB: f32`
- `SAFETY_DEFAULT_LOOKAHEAD_MS: f32`
- `SAFETY_DEFAULT_FADE_MS: f32`
- `SAFETY_DEFAULT_RELEASE_FAST_MS: f32`
- `SAFETY_DEFAULT_RELEASE_SLOW_MS: f32`
- `SAFETY_DEFAULT_HOLD_MS: f32`
- `SAFETY_MAX_SECONDS: f32`
- `SAFETY_DENORMAL: f32`
- `SAFETY_INF: f32`
- `FEEDBACK_HARD_LIMIT: f32`
- `FEEDBACK_SOFT_MAX: f32`

**Functions:**

| Name | Signature | Docs |
|------|-----------|------|
| `sample_is_bad` | `(x: f32) -> bool` | — |
| `flush_denormal` | `(x: f32) -> f32` | — |
| `true_peak_new` | `() -> TruePeak` | — |
| `true_peak_push` | `(d: ptr<TruePeak>, l: f32, r: f32) -> f32` | — |
| `true_peak_reset` | `(d: ptr<TruePeak>) -> void` | — |
| `limiter_new` | `(ceiling_db: f32, lookahead_ms: f32,
                            release_fast_ms: f32, release_slow_ms: f32,
                            hold_ms: f32, rate: SampleRate) -> Limiter` | — |
| `limiter_reset` | `(l: ptr<Limiter>) -> void` | — |
| `limiter_set_ceiling_db` | `(l: ptr<Limiter>, ceiling_db: f32) -> void` | — |
| `limiter_step` | `(l: ptr<Limiter>, in_l: f32, in_r: f32,
                             out_l: ptr<f32>, out_r: ptr<f32>) -> f32` | — |
| `limiter_gain` | `(l: ptr<Limiter>) -> f32` | — |
| `limiter_gain_reduction_db` | `(l: ptr<Limiter>) -> f32` | — |
| `limiter_max_gain_reduction_db` | `(l: ptr<Limiter>) -> f32` | — |
| `limiter_latency_samples` | `(l: ptr<Limiter>) -> i32` | — |
| `feedback_is_safe` | `(k: f32) -> bool` | A delay or reverb whose feedback coefficient reaches 1.0 never decays; past 1.0 it grows without bound. This is the single most common way a synth patch turns into a hazard, so it gets a guard rather than a comment. |
| `feedback_guard` | `(k: f32) -> f32` | Returns a coefficient that is safe to use. A magnitude at or above 1.0 is refused outright and becomes 0.0, because there is no sensible substitute for "make this louder forever". Between FEEDBACK_SOFT_MAX and 1.0 the value is clamped and the caller told. |
| `rt60_to_feedback` | `(rt60_seconds: f32, delay_seconds: f32) -> f32` | Feedback coefficient that decays 60 dB in `rt60_seconds`, for a loop whose round trip is `delay_seconds`. This is how you should ask for a tail: in time, not in a number between 0 and 1 that you guessed. |
| `feedback_to_rt60` | `(k: f32, delay_seconds: f32) -> f32` | The inverse: how long a given coefficient rings for. |
| `safety_config_default` | `() -> SafetyConfig` | — |
| `safety_config_ceiling` | `(cfg: SafetyConfig, ceiling_db: f32) -> SafetyConfig` | Deliberate ceiling override, for work that is going somewhere other than a stranger's headphones. Everything else stays default. |
| `safety_config_fades` | `(cfg: SafetyConfig, fade_in_ms: f32, fade_out_ms: f32) -> SafetyConfig` | — |
| `safety_new` | `(rate: SampleRate, seconds: f32) -> SafetyChain` | — |
| `safety_new_with` | `(rate: SampleRate, seconds: f32, cfg: SafetyConfig) -> SafetyChain` | — |
| `fade_gain` | `(t: f32) -> f32` | — |
| `safety_process_frame` | `(c: ptr<SafetyChain>, in_l: f32, in_r: f32) -> Frame` | — |
| `safety_process_block` | `(c: ptr<SafetyChain>, data: ptr<f32>, frames: i32) -> i32` | — |
| `safety_next_block` | `(c: ptr<SafetyChain>, max_block: i32) -> i32` | Frames left in the watchdog window, capped at `max_block`. Loop on this and the render is exactly as long as it said it would be. |
| `safety_reset` | `(c: ptr<SafetyChain>) -> void` | — |
| `safety_finished` | `(c: ptr<SafetyChain>) -> bool` | Chain readouts |
| `safety_total_frames` | `(c: ptr<SafetyChain>) -> i64` | — |
| `safety_frames_done` | `(c: ptr<SafetyChain>) -> i64` | — |
| `safety_duration_seconds` | `(c: ptr<SafetyChain>) -> f32` | — |
| `safety_watchdog_hit` | `(c: ptr<SafetyChain>) -> bool` | — |
| `safety_ceiling_db` | `(c: ptr<SafetyChain>) -> f32` | — |
| `safety_ceiling_linear` | `(c: ptr<SafetyChain>) -> f32` | — |
| `safety_latency_samples` | `(c: ptr<SafetyChain>) -> i32` | — |
| `safety_peak_in` | `(c: ptr<SafetyChain>) -> f32` | — |
| `safety_peak_in_db` | `(c: ptr<SafetyChain>) -> f32` | — |
| `safety_true_peak_in` | `(c: ptr<SafetyChain>) -> f32` | — |
| `safety_true_peak_in_db` | `(c: ptr<SafetyChain>) -> f32` | — |
| `safety_peak_out` | `(c: ptr<SafetyChain>) -> f32` | — |
| `safety_peak_out_db` | `(c: ptr<SafetyChain>) -> f32` | — |
| `safety_true_peak_out` | `(c: ptr<SafetyChain>) -> f32` | — |
| `safety_true_peak_out_db` | `(c: ptr<SafetyChain>) -> f32` | — |
| `safety_rms_in` | `(c: ptr<SafetyChain>) -> f32` | — |
| `safety_rms_in_db` | `(c: ptr<SafetyChain>) -> f32` | — |
| `safety_rms_out` | `(c: ptr<SafetyChain>) -> f32` | — |
| `safety_rms_out_db` | `(c: ptr<SafetyChain>) -> f32` | — |
| `safety_gain_reduction_db` | `(c: ptr<SafetyChain>) -> f32` | — |
| `safety_max_gain_reduction_db` | `(c: ptr<SafetyChain>) -> f32` | — |
| `safety_clamp_count` | `(c: ptr<SafetyChain>) -> i64` | — |
| `safety_nan_count` | `(c: ptr<SafetyChain>) -> i64` | — |
| `safety_muted` | `(c: ptr<SafetyChain>) -> bool` | — |
| `safety_ok` | `(c: ptr<SafetyChain>) -> bool` | True when the render came out clean: nothing over the ceiling, no NaN, and the hard clamp never had to save us. |
| `safety_report` | `(c: ptr<SafetyChain>) -> void` | — |

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

### `audio/sink.flow`

Audio Sink: one output target, device or file  Every audio example writes through a sink instead of talking to the device

**Structs:** `AudioSink`

**Constants:**

- `SINK_DEVICE: i32`
- `SINK_WAV: i32`
- `SINK_SILENT: i32`

**Functions:**

| Name | Signature | Docs |
|------|-----------|------|
| `sink_open` | `(rate: i32, channels: i32, block: i32) -> AudioSink` | Open the sink the environment asks for. |
| `sink_write` | `(s: ptr<AudioSink>, data: ptr<f32>, frames: i32) -> i32` | Write interleaved f32 frames. Returns frames accepted. |
| `sink_close` | `(s: ptr<AudioSink>) -> i64` | — |
| `sink_mode` | `(s: ptr<AudioSink>) -> i32` | — |
| `sink_is_offline` | `(s: ptr<AudioSink>) -> bool` | — |
| `sink_frames` | `(s: ptr<AudioSink>) -> i64` | — |
| `sink_is_render` | `() -> bool` | True when this run wrote a WAV, so the example can read it back and check it. Survives sink_close, which is when the file is finished and readable. |
| `sink_render_path` | `() -> string` | Path of the WAV this run wrote. Empty string when nothing was written. |

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

### `audio/verify.flow`

Offline render verification: how CI listens to audio without a sound card.  Every audio example can render to a WAV instead of opening a device

**Structs:** `VerifyReport`, `VerifySpec`

**Constants:**

- `VERIFY_MAX_BINS: i32`
- `VERIFY_BLOCK: i32`

**Functions:**

| Name | Signature | Docs |
|------|-----------|------|
| `verify_bank_clear` | `() -> void` | Goertzel bank |
| `verify_bank_add` | `(hz: f64) -> i32` | Append one analysis frequency. Returns its bin index, or -1 when full. |
| `verify_bank_count` | `() -> i32` | — |
| `verify_bank_freq` | `(i: i32) -> f64` | — |
| `verify_bank_tone` | `(expect_hz: f64, rate_hz: f64) -> i32` | Bin 0 is `expect_hz`; the rest is a semitone ladder that avoids it. |
| `verify_bank_power` | `(i: i32) -> f64` | Goertzel magnitude squared for one bin. |
| `verify_report_bad` | `() -> VerifyReport` | — |
| `verify_wav` | `(path: string, edge_frames: i32) -> VerifyReport` | Stream the whole file once and measure everything. `edge_frames` is the head/tail window used for the fade check. Call verify_bank_tone first if a tone check is wanted; pass expect_hz <= 0 through verify_run to skip it. |
| `verify_spec` | `(seconds: f64, ceiling_db: f32, expect_hz: f64) -> VerifySpec` | The usual spec: 48 kHz stereo, the safety chain's own ceiling and fade length, duration matched to 10 ms. Pass expect_hz <= 0 for material with no single pitch. |
| `verify_spec_rate` | `(spec: VerifySpec, rate: i32, channels: i32) -> VerifySpec` | — |
| `verify_spec_tolerance` | `(spec: VerifySpec, tol_seconds: f64) -> VerifySpec` | — |
| `verify_spec_fade` | `(spec: VerifySpec, fade_ms: f64) -> VerifySpec` | Only needed when the example overrode the safety chain's fade length. |
| `verify_run` | `(path: string, spec: VerifySpec) -> bool` | Read the render back and check it against the spec. Prints one line per check and returns true only if every line passed. This is the call an example gates its exit code on. |

### `audio/wav.flow`

WAV File I/O (32-bit IEEE float PCM)  Offline render target for the audio examples: everything that can play to a

**Structs:** `WavInfo`

**Constants:**

- `WAV_SEEK_SET: i32`
- `WAV_HEADER_BYTES: i64`
- `WAV_STAGE_FRAMES: i32`

**Functions:**

| Name | Signature | Docs |
|------|-----------|------|
| `wav_write_open` | `(path: string, rate: i32, channels: i32) -> bool` | Open a WAV file for writing. Returns false if the path cannot be created or another file is already open. |
| `wav_write_frames` | `(data: ptr<f32>, frames: i32) -> i32` | Append interleaved f32 frames. Returns frames written. |
| `wav_write_frame` | `(fr: Frame) -> i32` | Append one interleaved frame from a stereo Frame (channels must be 2). |
| `wav_write_close` | `() -> i64` | Patch the RIFF/data sizes and close. Returns frames written. |
| `wav_write_is_open` | `() -> bool` | — |
| `wav_write_frame_count` | `() -> i64` | — |
| `wav_info_bad` | `() -> WavInfo` | — |
| `wav_info_duration` | `(info: WavInfo) -> f64` | — |
| `wav_read_open` | `(path: string) -> WavInfo` | Open a canonical 44-byte-header WAV for streaming reads. Only the layout this module writes is accepted (float32, one "data" chunk at offset 36). |
| `wav_read_frames` | `(dst: ptr<f32>, frames: i32) -> i32` | Read up to `frames` interleaved f32 frames into `dst`. Returns frames read (0 at end of file). |
| `wav_read_close` | `() -> void` | — |
| `wav_read_is_open` | `() -> bool` | — |

### `audio.flow`

Audio Module - Core Types and Operations  Real-time audio processing primitives with proper DSP nomenclature.

**Structs:** `SampleRate`, `Samples`, `Seconds`, `Frame`, `Layout`, `Buffer`, `AudioBufferF32`

**Constants:**

- `DB_SILENCE: f32`

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
| `linear_to_db` | `(linear: f32) -> f32` | Convert linear amplitude to decibels: 20 * log10(linear). 1.0 -> 0 dB, 0.5 -> -6.02 dB, 0.0 (or negative) -> DB_SILENCE. |
| `db_to_linear` | `(db: f32) -> f32` | Convert decibels to linear amplitude: 10^(db/20). 0 dB -> 1.0, -6.02 dB -> 0.5, <= -96 dB -> 0.0 |
| `midi_to_freq` | `(note: i32) -> f32` | MIDI note to frequency (A4 = 69 = 440Hz): f = 440 * 2^((note - 69) / 12) Exact via powf; the old repeated-multiply version drifted by ~2.4e-4 relative over four octaves and only handled whole semitones. |
| `midi_to_freq_f` | `(note: f32) -> f32` | MIDI note to frequency with a fractional (pitch-bent / detuned) note number. |
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

### `automata.flow`

automata: a cellular-automaton framework.  Import: import "stdlib/automata.flow"

**Functions:**

| Name | Signature | Docs |
|------|-----------|------|
| `ca_seed` | `(s: i32) -> void` | — |
| `ca_rand_u32` | `() -> u32` | — |
| `ca_rand_below` | `(n: i32) -> i32` | Uniform on [0, n). |
| `ca_rand_unit` | `() -> f64` | Uniform on [0, 1). |
| `ca_fold` | `(i: i32, n: i32, bound: i32) -> i32` | Fold one axis index into range under `bound`. Returns -1 when the index is outside a fixed boundary. |
| `ca_get` | `(grid: ptr<i32>, w: i32, h: i32, x: i32, y: i32,
                       bound: i32, outside: i32) -> i32` | Read a cell, returning `outside` where a fixed boundary bites. |
| `ca_set` | `(grid: ptr<i32>, w: i32, h: i32, x: i32, y: i32,
                       v: i32) -> void` | — |
| `ca_nb_count` | `(nb: i32) -> i32` | ---------------------------------------------------------- neighbourhoods |
| `ca_nb_dx` | `(nb: i32, k: i32, x: i32, y: i32) -> i32` | Offsets depend on the cell for the two non-square tilings: hexagonal rows are staggered (odd-r), and a triangle points up or down by parity. |
| `ca_nb_dy` | `(nb: i32, k: i32, x: i32, y: i32) -> i32` | — |
| `ca_count_state` | `(grid: ptr<i32>, w: i32, h: i32, x: i32, y: i32,
                               nb: i32, bound: i32, state: i32) -> i32` | How many neighbours hold `state`. |
| `ca_nb_sum` | `(grid: ptr<i32>, w: i32, h: i32, x: i32, y: i32,
                          nb: i32, bound: i32, outside: i32) -> i32` | Sum over the neighbourhood, with `outside` counted where fixed. |
| `ca_elementary_bit` | `(rule: i32, l: i32, c: i32, r: i32) -> i32` | Wolfram's numbering: the rule byte's bit (4l + 2c + r) is the new centre. |
| `ca_elementary_step` | `(src: ptr<i32>, dst: ptr<i32>, n: i32,
                                   rule: i32, bound: i32) -> i32` | — |
| `ca_elementary_raster` | `(rows: ptr<i32>, n: i32, gens: i32,
                                     rule: i32, bound: i32) -> void` | Fill a `gens x n` raster, row 0 already holding the initial condition. The raster is the usual space-time diagram: time increases downward. |
| `ca_seed_single` | `(row: ptr<i32>, n: i32) -> void` | A single 1 in the middle of an otherwise empty row. |
| `ca_seed_random` | `(row: ptr<i32>, n: i32, nstates: i32) -> void` | — |
| `ca_totalistic_step` | `(src: ptr<i32>, dst: ptr<i32>, n: i32,
                                   k: i32, radius: i32, code: i32,
                                   bound: i32) -> i32` | k-state totalistic: the new value is digit (sum of the 2r+1 window) of the code written in base k. Radius 1, k = 3 gives Wolfram's totalistic codes. |
| `ca_outer_totalistic_step` | `(src: ptr<i32>, dst: ptr<i32>, n: i32,
                                         k: i32, radius: i32, code: i32,
                                         bound: i32) -> i32` | Outer totalistic: the centre keeps its own identity, so the code is indexed by (centre, outer sum) rather than by the total alone. |
| `ca_parse_bs` | `(spec: string, out: ptr<i32>) -> bool` | Parse B/S notation ("B3/S23", "b36/s23", "23/3" is not accepted) into two bitmasks: out[0] births, out[1] survivals, bit n meaning n neighbours. Returns false if the string names no neighbour counts or holds a character outside "BbSs0-9/ ". |
| `ca_bs_has` | `(mask: i32, count: i32) -> bool` | — |
| `ca_life_step` | `(src: ptr<i32>, dst: ptr<i32>, w: i32, h: i32,
                             birth: i32, survive: i32, nb: i32,
                             bound: i32) -> i32` | One synchronous life-like generation. Cells are 0 or 1. |
| `ca_life_step_mode` | `(src: ptr<i32>, dst: ptr<i32>, w: i32, h: i32,
                                  birth: i32, survive: i32, nb: i32,
                                  bound: i32, mode: i32,
                                  alpha_ppm: i32) -> i32` | The same rule under a chosen schedule. CA_SYNC            classic: dst is a full new generation CA_ASYNC_RANDOM    dst starts as a copy of src; each cell is offered an update with probability alpha_ppm / 1e6, and the |
| `ca_generations_step` | `(src: ptr<i32>, dst: ptr<i32>, w: i32,
                                    h: i32, birth: i32, survive: i32,
                                    nstates: i32, nb: i32, bound: i32) -> i32` | Multi-state "generations" rules. State 1 is alive; states 2 .. nstates-1 are the refractory tail, counting up and then dying; state 0 is empty. Only state-1 neighbours count. Brian's Brain is nstates 3 with B2/S. |
| `ca_cyclic_step` | `(src: ptr<i32>, dst: ptr<i32>, w: i32, h: i32,
                               nstates: i32, threshold: i32, nb: i32,
                               bound: i32) -> i32` | Greenberg-Hastings / cyclic CA: state s is eaten by s+1 mod nstates once `threshold` neighbours already hold s+1. |
| `ca_wireworld_step` | `(src: ptr<i32>, dst: ptr<i32>, w: i32,
                                  h: i32, bound: i32) -> i32` | Wireworld: head -> tail -> wire, and wire -> head when exactly one or two of its eight neighbours are heads. That single clause is what makes the rule a logic family rather than a decoration. |
| `ca_sandpile_sweep` | `(grid: ptr<i32>, delta: ptr<i32>, w: i32,
                                  h: i32, threshold: i32, bound: i32) -> i32` | One parallel toppling sweep of the abelian sandpile. Every site holding at least `threshold` grains gives one grain to each von Neumann neighbour; grains that leave a fixed boundary are lost. Returns the number of sites that toppled, so zero means the configuration is stable. |
| `ca_sandpile_avalanche` | `(grid: ptr<i32>, delta: ptr<i32>,
                                      touched: ptr<i32>, w: i32, h: i32,
                                      x: i32, y: i32, threshold: i32,
                                      bound: i32, max_sweeps: i32,
                                      stats: ptr<i32>) -> i32` | Drop one grain and relax to stability. Fills stats with the avalanche observables the scaling laws are stated in: stats[0] size      total topplings stats[1] duration  sweeps needed to return to stability |
| `ca_turmite_step` | `(grid: ptr<i32>, w: i32, h: i32, st: ptr<i32>,
                                table: ptr<i32>, ncolours: i32, bound: i32) -> i32` | — |
| `ca_langton_table` | `(out: ptr<i32>) -> void` | Langton's ant as a one-state, two-colour turmite: RL. |
| `ca_ant_table` | `(turns: string, out: ptr<i32>) -> i32` | A turmite table from a turn string over {L, R, N, U}: "RL" is Langton's ant, "RLR" and "LLRR" are the well-known multi-colour ants. Returns the number of colours, or 0 if the string holds an unknown letter. |
| `ca_margolus_step` | `(grid: ptr<i32>, w: i32, h: i32,
                                 table: ptr<i32>, parity: i32) -> void` | The Margolus neighbourhood partitions the grid into 2x2 blocks, offset by one cell on odd steps. A rule is a table of 16 entries mapping the block's 4-bit occupancy to the next one, with bit 0 top-left, bit 1 top-right, bit 2 bottom-left, bit 3 bottom-right. When the table is a permutation of |
| `ca_margolus_is_permutation` | `(table: ptr<i32>) -> bool` | — |
| `ca_margolus_invert` | `(table: ptr<i32>, inv: ptr<i32>) -> bool` | The inverse table, so the same stepper runs the CA backwards. |
| `ca_margolus_hpp_table` | `(out: ptr<i32>) -> void` | HPP lattice gas in Margolus form: every particle moves diagonally across its block (a 180 degree rotation), except that a pair meeting head-on along one diagonal leaves along the other. This is the billiard-ball model's collision, and the table is its own inverse. |
| `ca_margolus_critters_table` | `(out: ptr<i32>) -> void` | Critters (Toffoli and Margolus): complement the block, leave it alone when exactly two cells are on, and also rotate when exactly three are on. It is reversible and it has gliders. |
| `ca_margolus_tron_table` | `(out: ptr<i32>) -> void` | Tron: complement blocks that are uniform, leave everything else. Also an involution. |
| `ca_population` | `(grid: ptr<i32>, n: i32) -> i32` | ---------------------------------------------------------------- measures |
| `ca_count_value` | `(grid: ptr<i32>, n: i32, v: i32) -> i32` | — |
| `ca_density` | `(grid: ptr<i32>, n: i32) -> f64` | — |
| `ca_hamming` | `(a: ptr<i32>, b: ptr<i32>, n: i32) -> i32` | — |
| `ca_entropy` | `(grid: ptr<i32>, n: i32, nstates: i32,
                           bins: ptr<i32>) -> f64` | Shannon entropy of the state distribution, in bits per cell. `bins` must hold at least `nstates` entries and is used as scratch. |
| `ca_block_entropy` | `(row: ptr<i32>, n: i32, len: i32,
                                 bins: ptr<i32>) -> f64` | Block entropy of a binary row: Shannon entropy over the 2^len sliding windows, divided by len, so a maximally random row scores 1 bit per cell and a constant row scores 0. `bins` needs 2^len entries; len <= 12. |
| `ca_hash` | `(grid: ptr<i32>, n: i32) -> i64` | FNV-1a over the cell values: a configuration fingerprint for cycle detection. Two different configurations colliding is a 2^-64 event, and callers that cannot accept even that should compare the states directly once a hash matches. |
| `ca_cycle_find` | `(ring: ptr<i64>, len: i32, h: i64) -> i32` | Search a ring of past hashes for `h`; returns the slot, or -1. |
| `ca_find_cycle` | `(a: ptr<i32>, b: ptr<i32>, n: i32, rule: i32,
                              bound: i32, max_steps: i32, ring: ptr<i64>,
                              out: ptr<i32>) -> i32` | Run a 1D rule until the configuration repeats. Fills out[0] with the period and out[1] with the transient length, both -1 if nothing repeated within `max_steps`. `ring` must hold `max_steps` hashes. |
| `ca_input_entropy` | `(row: ptr<i32>, n: i32, bound: i32,
                                 bins: ptr<i32>) -> f64` | Shannon entropy, in bits, of how often each of the eight elementary neighbourhood patterns was looked up over one row. |
| `ca_classify` | `(rule: i32, width: i32, gens: i32, bound: i32,
                            wk: CAWork, evidence: ptr<f64>) -> i32` | — |
| `ca_class_name` | `(cls: i32) -> string` | — |
| `ca_blit_pack` | `(grid: ptr<i32>, w: i32, h: i32, px: i32,
                             pal: ptr<u8>, nstates: i32,
                             out: ptr<u8>) -> void` | Pack a grid into an RGB8 buffer for one gfx_blit_rgb call, scaling each cell to `px` by `px` device pixels. `pal` holds 3 bytes per state. A dense grid drawn cell by cell with fill_rect is tens of thousands of calls a frame; this is one. |

### `bigint.flow`

Big integer support for Project Euler (#252). Limb-based unsigned magnitude + separate sign. Ops are functions (no operator overloading yet). Enough for factorial / binomial / mod_pow style problems.

*No `export` items found (internal / extern-only module).*

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

### `checked_arith.flow`

Checked / saturating / wrapping integer arithmetic (#275). Prefer these helpers when you need defined overflow behaviour outside the safety-profile default (which aborts via FLOW_CHECKED_*).

*No `export` items found (internal / extern-only module).*

### `circuit.flow`

MODIFIED NODAL ANALYSIS: a small circuit simulator core, in Flow.  WHY A MATRIX AND NOT A `flow` BLOCK

**Functions:**

| Name | Signature | Docs |
|------|-----------|------|
| `circ_reset` | `() -> bool` | Clear the netlist. Every program starts here. |
| `circ_error` | `() -> i32` | — |
| `circ_add_r` | `(n1: i32, n2: i32, ohms: f64) -> i32` | — |
| `circ_add_c` | `(n1: i32, n2: i32, farads: f64, v0: f64) -> i32` | Capacitor with an initial voltage (used only when circ_tran_init(true)). |
| `circ_add_l` | `(n1: i32, n2: i32, henries: f64, i0: f64) -> i32` | Inductor with an initial current (flowing n1 -> n2). |
| `circ_add_v` | `(n1: i32, n2: i32, volts: f64) -> i32` | — |
| `circ_add_i` | `(n1: i32, n2: i32, amps: f64) -> i32` | Current amps flows into n1, through the source, out of n2 (SPICE sign). |
| `circ_add_e` | `(n1: i32, n2: i32, c1: i32, c2: i32,
                           gain: f64) -> i32` | VCVS: v(n1) - v(n2) = gain * (v(c1) - v(c2)) |
| `circ_add_g` | `(n1: i32, n2: i32, c1: i32, c2: i32,
                           gm: f64) -> i32` | VCCS: current gm * (v(c1) - v(c2)) flows into n1 and out of n2. |
| `circ_add_d` | `(n1: i32, n2: i32, is_sat: f64, nvt: f64) -> i32` | Diode: i = Is * (exp(v / (n*VT)) - 1), anode n1, cathode n2. |
| `circ_add_q` | `(nc: i32, nb: i32, ne: i32, is_sat: f64,
                           bf: f64, br: f64, vt: f64) -> i32` | NPN BJT, Ebers-Moll transport form. Terminals collector, base, emitter. |
| `circ_set_value` | `(e: i32, val: f64) -> void` | Change an element value in place (a source waveform, a switch resistance). |
| `circ_get_value` | `(e: i32) -> f64` | — |
| `circ_set_method` | `(m: i32) -> void` | — |
| `circ_set_gmin` | `(g: f64) -> void` | — |
| `circ_set_tol` | `(reltol: f64, abstol: f64) -> void` | — |
| `circ_set_maxiter` | `(n: i32) -> void` | — |
| `circ_finalize` | `() -> bool` | Assign branch-current rows and fix the matrix order. Returns false when a cap is exceeded. |
| `circ_dim_of` | `() -> i32` | — |
| `circ_node_count` | `() -> i32` | — |
| `circ_v` | `(node: i32) -> f64` | — |
| `circ_vd` | `(n1: i32, n2: i32) -> f64` | — |
| `circ_iterations` | `() -> i32` | — |
| `circ_worst_iterations` | `() -> i32` | — |
| `circ_solve_count` | `() -> i32` | — |
| `circ_factor_count` | `() -> i32` | — |
| `circ_reject_count` | `() -> i32` | — |
| `circ_i` | `(e: i32) -> f64` | Branch current of element e, in the n1 -> n2 direction (collector current for a BJT). |
| `circ_ib` | `(e: i32) -> f64` | Base current of a BJT. |
| `circ_state` | `(e: i32) -> f64` | The state variable of a reactive element: capacitor voltage or inductor current at the last accepted point. |
| `circ_op` | `() -> bool` | DC operating point |
| `circ_tran_init` | `(use_ic: bool, dt_prime: f64) -> bool` | Prepare for transient analysis. With use_ic the reactive states start from the values passed to circ_add_c / circ_add_l; otherwise they start from the DC operating point. The trapezoidal companion model needs the branch derivative at t = 0 as well |
| `circ_tran_step` | `(dt: f64) -> bool` | One fixed step. Returns false if Newton or LU failed. |
| `circ_time_now` | `() -> f64` | — |
| `circ_tran_step_adaptive` | `(dt_try: f64, tol: f64,
                                        dt_min: f64, dt_max: f64) -> f64` | Adaptive step by step doubling: one step of dt against two of dt/2. The error estimate is the largest normalized difference between the two results over the reactive state variables. Returns the step actually taken, or 0.0 on failure; circ_next_dt() suggests the next trial step. |
| `circ_next_dt` | `() -> f64` | — |

### `collections.flow`

FLOW Collections Standard Library HashMap, Set, Queue, Stack, Vector

*No `export` items found (internal / extern-only module).*

### `concurrent.flow`

FLOW Concurrency Standard Library Threads, mutexes, channels, atomics — real pthread/atomic backends. See docs/language/concurrency-vs-go.md

*No `export` items found (internal / extern-only module).*

### `crypto.flow`

Cryptographic primitives (FFI to platform or bundled implementations)

*No `export` items found (internal / extern-only module).*

### `dsp.flow`

DSP Pipeline Module  Functional DSP primitives that compose with the |> operator.

**Functions:**

| Name | Signature | Docs |
|------|-----------|------|
| `map_f32` | `(arr: ptr<f32>, n: i32, f: (f32) -> f32) -> ptr<f32>` | Apply a function element-wise: out[i] = f(arr[i]). |
| `filter_f32` | `(arr: ptr<f32>, n: i32, pred: (f32) -> bool, out_n: ptr<i32>) -> ptr<f32>` | Keep only elements where pred returns true. Returns a pointer; writes the filtered count to out_n. |
| `reduce_f32` | `(arr: ptr<f32>, n: i32, init: f32, f: (f32, f32) -> f32) -> f32` | Left fold: acc = f(acc, arr[0]), then f(acc, arr[1]), etc. |
| `scan_f32` | `(arr: ptr<f32>, n: i32, init: f32, f: (f32, f32) -> f32) -> ptr<f32>` | Prefix scan: out[0] = init, out[i] = f(out[i-1], arr[i]). |
| `zip_with_f32` | `(a: ptr<f32>, b: ptr<f32>, n: i32, f: (f32, f32) -> f32) -> ptr<f32>` | Element-wise combine two buffers: out[i] = f(a[i], b[i]). |
| `scale_f32` | `(arr: ptr<f32>, n: i32, gain: f32) -> ptr<f32>` | Scale every element by a scalar gain. |
| `offset_f32` | `(arr: ptr<f32>, n: i32, dc: f32) -> ptr<f32>` | Add a constant offset to every element. |
| `clip_f32` | `(arr: ptr<f32>, n: i32, lo: f32, hi: f32) -> ptr<f32>` | Clip elements to [lo, hi]. |
| `sum_f32` | `(arr: ptr<f32>, n: i32) -> f32` | Sum all elements. |
| `dot_f32` | `(a: ptr<f32>, b: ptr<f32>, n: i32) -> f32` | Dot product of two buffers. |
| `map_f64` | `(arr: ptr<f64>, n: i32, f: (f64) -> f64) -> ptr<f64>` | f64 primitives |
| `reduce_f64` | `(arr: ptr<f64>, n: i32, init: f64, f: (f64, f64) -> f64) -> f64` | — |
| `scan_f64` | `(arr: ptr<f64>, n: i32, init: f64, f: (f64, f64) -> f64) -> ptr<f64>` | — |
| `zip_with_f64` | `(a: ptr<f64>, b: ptr<f64>, n: i32, f: (f64, f64) -> f64) -> ptr<f64>` | — |
| `scale_f64` | `(arr: ptr<f64>, n: i32, gain: f64) -> ptr<f64>` | — |
| `sum_f64` | `(arr: ptr<f64>, n: i32) -> f64` | — |
| `dot_f64` | `(a: ptr<f64>, b: ptr<f64>, n: i32) -> f64` | — |

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

### `experiment.flow`

experiment: running behavioural and psychophysical experiments in Flow.  The case for compiling an experiment rather than interpreting it is narrow

**Structs:** `XpOnset`, `XpResponse`

**Constants:**

- `XP_KEY_A: i32`
- `XP_KEY_S: i32`
- `XP_KEY_D: i32`
- `XP_KEY_F: i32`
- `XP_KEY_Z: i32`
- `XP_KEY_X: i32`
- `XP_KEY_C: i32`
- `XP_KEY_V: i32`
- `XP_KEY_B: i32`
- `XP_KEY_1: i32`
- `XP_KEY_2: i32`
- `XP_KEY_3: i32`
- `XP_KEY_4: i32`
- `XP_KEY_J: i32`
- `XP_KEY_K: i32`
- `XP_KEY_L: i32`
- `XP_KEY_M: i32`
- `XP_KEY_N: i32`
- `XP_KEY_RETURN: i32`
- `XP_KEY_SPACE: i32`
- `XP_FIXATION: i32`
- `XP_STIMULUS: i32`
- `XP_FEEDBACK: i32`
- `XP_DONE: i32`

**Functions:**

| Name | Signature | Docs |
|------|-----------|------|
| `xp_now_ns` | `() -> i64` | Nanoseconds on the monotonic clock. Never goes backwards, unaffected by NTP steps or the user changing the system time mid-session. |
| `xp_ms_to_ns` | `(ms: f64) -> i64` | — |
| `xp_ns_to_ms` | `(ns: i64) -> f64` | — |
| `xp_ns_to_us` | `(ns: i64) -> f64` | — |
| `xp_clock_resolution_ns` | `(samples: i32) -> i64` | Smallest nonzero clock increment observed over `samples` back-to-back reads. This is the floor on reaction-time resolution: an RT cannot be reported finer than the clock can tick. |
| `xp_refresh_set` | `(hz: f64) -> void` | Nominal display refresh, used by xp_align_to_frame. This is what the display is *told* to be; nothing here verifies it against the panel. |
| `xp_refresh_hz_get` | `() -> f64` | — |
| `xp_frame_ns` | `() -> i64` | — |
| `xp_epoch_mark` | `() -> i64` | Start of the frame grid. Call once, after the window is up. |
| `xp_align_to_frame` | `(t_ns: i64) -> i64` | Round a target time up to the next nominal refresh boundary. Without a vsync callback this is a grid, not a guarantee; see the honesty section of docs/library/experiments.md. |
| `xp_onset_reset` | `() -> void` | — |
| `xp_onset_n` | `() -> i32` | — |
| `xp_onset_mean_us` | `() -> f64` | — |
| `xp_onset_sd_us` | `() -> f64` | — |
| `xp_onset_worst_us` | `() -> f64` | Worst absolute onset error seen since the last reset. This is the number a reviewer should be shown, not the mean. |
| `xp_onset_last_us` | `() -> f64` | — |
| `xp_wait_until` | `(target_ns: i64) -> i64` | Sleep coarsely, then spin, until the monotonic clock reaches target_ns. Handing the last two milliseconds to a spin loop is the whole trick: the scheduler will not wake a thread to better than about a millisecond, and a millisecond is six percent of a 60 Hz frame. |
| `xp_present_at` | `(target_ns: i64) -> XpOnset` | Wait for the target instant and count the miss against the onset statistics. Call this immediately before drawing, so the returned error is the onset error of the frame you are about to present. Use xp_wait_until instead for waits that are not stimulus onsets (frame pacing, inter-block pauses), so |
| `xp_seed` | `(seed: u32) -> u32` | — |
| `xp_seed_of_record` | `() -> u32` | The seed that was actually installed. Log it with the data; an experiment whose randomisation cannot be regenerated is not reproducible. |
| `xp_rand` | `() -> f64` | — |
| `xp_rand_int` | `(n: i32) -> i32` | — |
| `xp_rand_normal` | `() -> f64` | — |
| `xp_rand_exp` | `(mean: f64) -> f64` | — |
| `xp_ex_gaussian` | `(mu: f64, sigma: f64, tau: f64) -> f64` | Ex-Gaussian reaction time: Gaussian(mu, sigma) plus Exponential(tau). This is the standard descriptive RT distribution (Ratcliff 1979); tau supplies the right tail that a plain Gaussian cannot. |
| `xp_design_reset` | `() -> void` | — |
| `xp_factor` | `(levels: i32) -> i32` | Add a factor with `levels` levels. Returns its index, or -1 if the design is already full. Level codes are 0 .. levels-1 throughout. |
| `xp_nfactors` | `() -> i32` | — |
| `xp_nlevels` | `(factor: i32) -> i32` | — |
| `xp_design_build` | `(reps: i32) -> i32` | Cross every factor with every other, `reps` times. Trials come out in systematic order; call xp_shuffle to randomise. Returns the trial count, or -1 if the design does not fit. |
| `xp_ntrials` | `() -> i32` | — |
| `xp_ncells` | `() -> i32` | — |
| `xp_level` | `(pos: i32, factor: i32) -> i32` | Level of `factor` on the trial presented at position `pos`. |
| `xp_cell` | `(pos: i32) -> i32` | Cell index (the position in the systematic cross) of the trial at `pos`. |
| `xp_blocks` | `(n: i32) -> bool` | Split the trial list into n equal blocks. Returns false if the trial count does not divide evenly, because a ragged last block quietly unbalances a design and that should be an error, not a rounding. |
| `xp_nblocks_get` | `() -> i32` | — |
| `xp_block_of` | `(pos: i32) -> i32` | — |
| `xp_practice` | `(n: i32) -> void` | Mark the first n positions as practice. They are presented and logged like any other trial; the analysis is expected to drop them. |
| `xp_is_practice` | `(pos: i32) -> bool` | — |
| `xp_npractice_get` | `() -> i32` | — |
| `xp_shuffle` | `(seed: u32) -> u32` | Fisher-Yates over the whole presentation order. The seed is stored and returned so it can go in the data file and regenerate the exact sequence. |
| `xp_shuffle_within_blocks` | `(seed: u32) -> u32` | Shuffle within each block, so the block structure survives randomisation. |
| `xp_shuffle_seed_get` | `() -> u32` | — |
| `xp_latin` | `(n: i32, row: i32, pos: i32) -> i32` | Balanced Latin square (Williams design): condition to run at position `pos` for the participant in row `row`, with `n` conditions. Every condition appears once per row and once per column, and for even n every ordered pair of conditions is immediately adjacent exactly once, which |
| `xp_latin_balanced` | `(n: i32) -> bool` | — |
| `xp_response_miss` | `(timeout_ms: f64, onset_err_us: f64) -> XpResponse` | — |
| `xp_response_make` | `(key: i32, rt_ms: f64, expected: i32,
                                 onset_err_us: f64) -> XpResponse` | — |
| `xp_isi_ns` | `(min_ms: f64, jitter_ms: f64) -> i64` | Fixation duration is jittered so the participant cannot use a rhythm to predict onset, which is the single most common way an RT effect leaks away. |
| `xp_trial_begin` | `(fix_ms: f64, jitter_ms: f64, timeout_ms: f64,
                               feedback_ms: f64, expected: i32) -> void` | — |
| `xp_trial_state` | `() -> i32` | — |
| `xp_trial_onset_ns` | `() -> i64` | — |
| `xp_trial_result` | `() -> XpResponse` | — |
| `xp_trial_poll` | `(g: Gfx, k0: i32, k1: i32, k2: i32, k3: i32) -> i32` | Call once per frame, after gfx_poll and before drawing. Returns the state to draw. The stimulus onset time is stamped on the first frame in which the state is XP_STIMULUS, which is the frame the caller then draws and presents; the residual is the present-to-photon latency, which software |
| `xp_response_sim` | `(onset: XpOnset, key: i32, rt_ms: f64,
                                expected: i32, timeout_ms: f64) -> XpResponse` | Simulated participant. The presentation wait is real, so onset_err_us is a real measurement of this machine; the key and the RT come from the caller's responder model. Nothing here pretends a finger was involved. |
| `xp_fmt_reset` | `() -> void` | — |
| `xp_fmt_str` | `(s: string) -> void` | — |
| `xp_fmt_i32` | `(v: i32) -> void` | — |
| `xp_fmt_f64` | `(v: f64, decimals: i32) -> void` | Fixed-point, `decimals` places, round-half-up with carry. Written out here rather than handed to printf so a CSV row is byte-identical everywhere. |
| `xp_fmt_len` | `() -> i32` | — |
| `xp_mkdir_for` | `(dir: string) -> bool` | Create the directory a path lives in, walking each `/`-separated prefix so it behaves like `mkdir -p`. An existing directory is success, not an error. This calls mkdir(2) rather than shelling out: the transpiler emits a prototype for every extern, and a `system` prototype collides with the one |
| `xp_log_open` | `(path: string) -> bool` | Open the data file and write the header. Column set is fixed so that a reader never has to guess: unused factor columns hold -1. subject,block,trial,practice,f0,f1,f2,f3,response,rt_ms,correct,onset_err_us |
| `xp_log_is_open` | `() -> bool` | — |
| `xp_log_row` | `(subject: i32, pos: i32, resp: XpResponse) -> bool` | Write one trial. `pos` is the presentation position, so the factor levels and the block come from the design rather than from the caller restating them. |
| `xp_log_rows` | `() -> i32` | — |
| `xp_log_close` | `() -> void` | — |
| `xp_timing_write` | `(path: string, label: string) -> bool` | Write the timing report. Kept out of stdout on purpose: these numbers are a property of the machine and the run, and stdout has to stay byte-identical for the CI gate. Returns false if the file could not be written. |
| `xp_fixation` | `(g: Gfx, cx: i32, cy: i32, arm: i32, thick: i32,
                            r: i32, gr: i32, b: i32) -> void` | A fixation cross: two bars, centred, drawn in one call so every paradigm gets the same one. |
| `xp_center_text` | `(g: Gfx, cx: i32, y: i32, s: string, scale: i32,
                               r: i32, gr: i32, b: i32) -> void` | — |
| `xp_instruction_panel` | `(g: Gfx, w: i32, h: i32, title: string) -> void` | Instruction screen scaffolding: a panel, a title, then numbered lines the caller adds with xp_instruction_line. |
| `xp_instruction_line` | `(g: Gfx, x: i32, y: i32, s: string,
                                    r: i32, gr: i32, b: i32) -> void` | — |
| `xp_progress` | `(g: Gfx, x: i32, y: i32, w: i32, h: i32,
                            done: i32, total: i32) -> void` | Progress bar over the block: filled fraction is trials done over total. |
| `xp_feedback_bar` | `(g: Gfx, cx: i32, y: i32, w: i32, h: i32,
                                resp: XpResponse) -> void` | Correct / incorrect / too-slow feedback, as a coloured bar under fixation. |

### `fmm2d.flow`

fmm2d: Carrier-Greengard-Rokhlin adaptive Fast Multipole Method in 2D.  Implements the analytic apparatus of

**Functions:**

| Name | Signature | Docs |
|------|-----------|------|
| `fmm2d_configure` | `(p: i32, s: i32) -> void` | — |
| `fmm2d_set_particles` | `(n: i32, x: ptr<f64>, y: ptr<f64>, q: ptr<f64>) -> bool` | — |
| `fmm2d_evaluate` | `() -> bool` | — |
| `fmm2d_direct_evaluate` | `() -> bool` | — |
| `fmm2d_rel_field_error` | `() -> f64` | Paper-style relative field error: \|\|E_fmm - E_dir\|\|_2 / \|\|E_dir\|\|_2 |
| `fmm2d_max_rel_error` | `() -> f64` | — |
| `fmm2d_potential` | `(i: i32) -> f64` | — |
| `fmm2d_ex` | `(i: i32) -> f64` | — |
| `fmm2d_ey` | `(i: i32) -> f64` | — |
| `fmm2d_nboxes` | `() -> i32` | — |
| `fmm2d_nleaves` | `() -> i32` | — |
| `fmm2d_max_level` | `() -> i32` | — |
| `fmm2d_time_ms` | `() -> f64` | — |
| `fmm2d_direct_time_ms` | `() -> f64` | — |
| `fmm2d_m2l_count` | `() -> f64` | — |
| `fmm2d_p2p_count` | `() -> f64` | — |
| `fmm2d_box_cx` | `(b: i32) -> f64` | — |
| `fmm2d_box_cy` | `(b: i32) -> f64` | — |
| `fmm2d_box_h` | `(b: i32) -> f64` | — |
| `fmm2d_box_half` | `(b: i32) -> f64` | — |
| `fmm2d_box_leaf` | `(b: i32) -> i32` | — |
| `fmm2d_box_level` | `(b: i32) -> i32` | — |
| `fmm2d_particle_x` | `(i: i32) -> f64` | — |
| `fmm2d_particle_y` | `(i: i32) -> f64` | — |
| `fmm2d_particle_q` | `(i: i32) -> f64` | — |
| `fmm2d_n` | `() -> i32` | — |
| `fmm2d_p` | `() -> i32` | — |
| `fmm2d_s` | `() -> i32` | — |

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
| `gfx_blit_rgb` | `(g: Gfx, x: i32, y: i32, w: i32, h: i32, src: ptr<u8>) -> void` | Blit a packed RGB8 buffer (w*h*3 bytes, row-major) at (x, y). Per-pixel fields — particle sands, software rasterizers, image filters — should build a buffer and blit it once per frame. A fill_rect per pixel is tens of thousands of calls a frame and will not keep up. |
| `gfx_present` | `(g: Gfx) -> void` | — |
| `gfx_frame_pump` | `(g: Gfx) -> bool` | Poll events; return false if the window should close or Esc is down. |
| `gfx_run` | `(g: Gfx, max_frames: i32) -> i32` | Run up to max_frames, calling user-defined flow_gfx_frame(ctx, frame) each tick. Returns the number of frames completed. Requires linking the gfx runtime. |
| `gfx_time_ms` | `(g: Gfx) -> f64` | Milliseconds since the window opened. The clock lives on the gfx ABI rather than in stdlib/time.flow because it has to mean the right thing in every build mode, and the backends disagree on purpose: |
| `gfx_wait_frame` | `(g: Gfx, target_fps: i32) -> void` | Sleep out the remainder of the current frame at target_fps. There is no vsync on the native paths, so without this a demo runs as fast as the machine allows and its speed becomes hardware-dependent. No-op in the recorder (which should run flat out) and in the browser (where present |
| `gfx_mouse` | `(g: Gfx) -> Mouse` | — |
| `gfx_mouse_x` | `(g: Gfx) -> i32` | — |
| `gfx_mouse_y` | `(g: Gfx) -> i32` | — |
| `gfx_mouse_down` | `(g: Gfx, button: i32) -> bool` | button: 0 = left, 1 = right, 2 = middle |
| `gfx_mouse_wheel` | `(g: Gfx) -> i32` | Cumulative scroll total. Diff against your own previous value. |

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
| `gpu_mul_f32` | `(out: GpuBuffer, a: GpuBuffer, b: GpuBuffer, n: i64) -> i32` | Elementwise multiply kernels (Metal on macOS, -1 from the stub elsewhere). The backward pair is the same kernel with different operands: grad_a = grad_out * b, grad_b = grad_out * a. |
| `gpu_mul_backward_a_f32` | `(grad_a: GpuBuffer, grad_out: GpuBuffer, b: GpuBuffer, n: i64) -> i32` | — |
| `gpu_mul_backward_b_f32` | `(grad_b: GpuBuffer, grad_out: GpuBuffer, a: GpuBuffer, n: i64) -> i32` | — |
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

### `keys.flow`

Keyboard constants for gfx programs.  Every backend speaks macOS NSEvent virtual keycodes, because that is what the

*No `export` items found (internal / extern-only module).*

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

**Structs:** `Arena`, `FrameArena`

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
| `grow_uninit` | `(p: ptr<void>, new_size: i64) -> ptr<void>` | ── Uninitialized growth helpers (#424) ───────────────────────────── realloc without zeroing the new region. Callers must initialize every new element before reading it. Use grow_zeroed when zero-fill is needed. |
| `grow_zeroed` | `(p: ptr<void>, old_size: i64, new_size: i64) -> ptr<void>` | — |
| `alloc_uninit` | `(elem_size: i64, count: i64) -> ptr<void>` | Allocate exactly count * elem_size bytes, no minimum capacity floor. Callers must initialize elements before reading. |
| `arena_create` | `(capacity: i64) -> Arena` | — |
| `arena_alloc` | `(arena: ptr<Arena>, size: i64) -> ptr<void>` | — |
| `arena_alloc_i32` | `(arena: ptr<Arena>, count: i64) -> ptr<i32>` | — |
| `arena_alloc_f32` | `(arena: ptr<Arena>, count: i64) -> ptr<f32>` | — |
| `arena_reset` | `(arena: ptr<Arena>) -> void` | — |
| `arena_destroy` | `(arena: ptr<Arena>) -> void` | — |
| `arena_used` | `(arena: Arena) -> i64` | — |
| `arena_remaining` | `(arena: Arena) -> i64` | — |
| `frame_arena_create` | `(capacity: i64) -> FrameArena` | — |
| `frame_arena_destroy` | `(f: ptr<FrameArena>) -> void` | — |
| `frame_begin` | `(f: ptr<FrameArena>) -> void` | Reset the frame. This is the whole deallocation. |
| `frame_alloc` | `(f: ptr<FrameArena>, size: i64) -> ptr<void>` | — |
| `frame_alloc_i32` | `(f: ptr<FrameArena>, count: i64) -> ptr<i32>` | — |
| `frame_alloc_f32` | `(f: ptr<FrameArena>, count: i64) -> ptr<f32>` | — |
| `frame_alloc_f64` | `(f: ptr<FrameArena>, count: i64) -> ptr<f64>` | — |
| `frame_end` | `(f: ptr<FrameArena>) -> void` | Close the frame: record the high-water mark so a fixed capacity can be sized from a real run, and count the frame. |
| `frame_used` | `(f: FrameArena) -> i64` | — |
| `frame_remaining` | `(f: FrameArena) -> i64` | — |
| `frame_high_water` | `(f: FrameArena) -> i64` | — |
| `frame_count` | `(f: FrameArena) -> i64` | — |

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

### `planet.flow`

planet: a procedural planet as a system that evolves through time.  A planet is not a texture. It is the fixed point of a few slow processes

**Functions:**

| Name | Signature | Docs |
|------|-----------|------|
| `pl_minf` | `(a: f32, b: f32) -> f32` | Scalar helpers |
| `pl_maxf` | `(a: f32, b: f32) -> f32` | — |
| `pl_clampf` | `(v: f32, lo: f32, hi: f32) -> f32` | — |
| `pl_smoothstep` | `(e0: f32, e1: f32, x: f32) -> f32` | — |
| `pl_lerpf` | `(a: f32, b: f32, t: f32) -> f32` | — |
| `planet_seed` | `(s: u32) -> void` | Deterministic RNG: a 32-bit LCG (Numerical Recipes constants). |
| `planet_current_seed` | `() -> u32` | — |
| `pvec3` | `(x: f32, y: f32, z: f32) -> PVec3` | Vector helpers |
| `pv_norm` | `(a: PVec3) -> PVec3` | — |
| `pv_dot` | `(a: PVec3, b: PVec3) -> f32` | — |
| `pv_cross` | `(a: PVec3, b: PVec3) -> PVec3` | — |
| `pv_sub` | `(a: PVec3, b: PVec3) -> PVec3` | — |
| `planet_cell_at_dir` | `(dx: f32, dy: f32, dz: f32) -> i32` | Inverse cubesphere lookup: the cell containing a direction. |
| `planet_cell_at_lonlat` | `(lon_deg: f32, lat_deg: f32) -> i32` | — |
| `planet_init` | `() -> bool` | — |
| `planet_stage_ms` | `(slot: i32) -> f32` | — |
| `planet_stage_grid` | `() -> void` | Stage 1. Sample positions, cell areas and the eight-neighbour graph. |
| `planet_cell_dist` | `(i: i32, j: i32) -> f32` | Great-circle distance between two cells, kilometres. |
| `planet_cell_area_km2` | `(i: i32) -> f32` | — |
| `planet_cells` | `() -> i32` | — |
| `planet_face_n` | `() -> i32` | — |
| `planet_pos_x` | `(i: i32) -> f32` | — |
| `planet_pos_y` | `(i: i32) -> f32` | — |
| `planet_pos_z` | `(i: i32) -> f32` | — |
| `planet_pos` | `(i: i32) -> PVec3` | — |
| `planet_neighbor` | `(i: i32, d: i32) -> i32` | — |
| `planet_lat` | `(i: i32) -> f32` | Latitude in degrees, +90 at +Y. |
| `planet_lon` | `(i: i32) -> f32` | — |
| `planet_total_area` | `() -> f32` | Total solid angle, which must come to 4 pi. The evidence program checks it. |
| `planet_area_min` | `() -> f32` | — |
| `planet_area_max` | `() -> f32` | — |
| `planet_stage_tectonics` | `(nplates: i32) -> void` | — |
| `planet_plate` | `(i: i32) -> i32` | — |
| `planet_plate_count` | `() -> i32` | — |
| `planet_boundary` | `(i: i32) -> i32` | — |
| `planet_tectonic` | `(i: i32) -> f32` | — |
| `planet_plate_continental` | `(p: i32) -> bool` | — |
| `planet_boundary_length_km` | `() -> f32` | Total length of plate boundaries, kilometres. Counts each shared edge once by only looking at the four orthogonal neighbours and requiring i < n. |
| `planet_stage_elevation` | `() -> void` | — |
| `planet_set_sea_level_by_land_fraction` | `(target: f32) -> void` | Choose the sea-level datum so the land fraction hits `target`, then shift every elevation so sea level is exactly 0. Bisection on the area-weighted land fraction: 40 halvings on a 20 km bracket resolves to under a micrometre, so the answer is exact for f32. |
| `planet_measure_land_fraction` | `() -> f32` | — |
| `planet_elev` | `(i: i32) -> f32` | — |
| `planet_is_land` | `(i: i32) -> bool` | — |
| `planet_sea_datum` | `() -> f32` | — |
| `planet_land_fraction` | `() -> f32` | — |
| `planet_set_target_land` | `(t: f32) -> void` | — |
| `planet_set_relief` | `(r: f32) -> void` | — |
| `planet_set_erosion` | `(k: f32, m: f32, uplift: f32, diff: f32) -> void` | — |
| `planet_hypsometric` | `(e: f32) -> f32` | Area-weighted fraction of the sphere at or below `e` kilometres. This is the hypsometric curve, evaluated pointwise. |
| `planet_hypsometric_hist` | `(lo: f32, hi: f32, bins: i32,
                                        out: ptr<f32>) -> void` | Area-weighted elevation histogram: bin count in [lo, hi) split `bins` ways, written as fractions into `out`. |
| `planet_flood` | `() -> void` | Priority flood. Fills pl_w (the depression-free surface) and pl_order (the pop order, ascending in pl_w). |
| `planet_route` | `() -> void` | Steepest descent on the filled surface. Ocean cells are terminal. |
| `planet_accumulate` | `() -> void` | Upstream drainage area and longest upstream flow path, in one reverse pass over the flood order (which is descending in pl_w, so every contributor is already accumulated when its receiver is reached). |
| `planet_stage_erosion` | `(iters: i32) -> void` | Stage 4. `iters` rounds of flood, route, accumulate, incise, diffuse. |
| `planet_erode_step` | `() -> void` | One erosion round, exposed so the evolution demo can step it live. |
| `planet_flow_km2` | `(i: i32) -> f32` | — |
| `planet_flow_len_km` | `(i: i32) -> f32` | — |
| `planet_downstream` | `(i: i32) -> i32` | — |
| `planet_filled` | `(i: i32) -> f32` | — |
| `planet_lake_depth` | `(i: i32) -> f32` | — |
| `planet_measure_hack` | `(min_area_km2: f32) -> f32` | — |
| `planet_hack_exponent` | `() -> f32` | — |
| `planet_hack_intercept` | `() -> f32` | — |
| `planet_hack_r2` | `() -> f32` | — |
| `planet_hack_samples` | `() -> i32` | — |
| `planet_stage_climate` | `() -> void` | — |
| `planet_temp` | `(i: i32) -> f32` | — |
| `planet_precip` | `(i: i32) -> f32` | — |
| `planet_coast_dist` | `(i: i32) -> f32` | — |
| `planet_upwind` | `(i: i32) -> i32` | — |
| `planet_mean_land_precip` | `() -> f32` | — |
| `planet_rain_shadow_ratio` | `(hmin: f32) -> f32` | Rain-shadow evidence. Over every land cell above `hmin` kilometres that is on a slope, compare the mean precipitation where the wind is climbing (windward) against where it is descending (leeward). A real orographic model gives a ratio well above one; a noise field gives one. |
| `planet_classify_biome` | `(elev: f32, temp: f32, precip: f32,
                                      lake: f32) -> i32` | STAGE 6 --- biomes Whittaker's classification: mean annual temperature against annual precipitation, with the polar and alpine cutoffs that Whittaker's diagram leaves implicit. Precipitation thresholds are in millimetres per year. |
| `planet_stage_biomes` | `() -> void` | — |
| `planet_biome` | `(i: i32) -> i32` | — |
| `planet_biome_name` | `(b: i32) -> string` | — |
| `planet_biome_r` | `(b: i32) -> f32` | — |
| `planet_biome_g` | `(b: i32) -> f32` | — |
| `planet_biome_b` | `(b: i32) -> f32` | — |
| `planet_biome_land_fraction` | `(b: i32) -> f32` | Area-weighted fraction of land covered by biome `b`. Lakes count as land. |
| … | 14 more | |

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

### `procgen.flow`

procgen: self-contained 2D/3D gradient and value noise for general use.  A procedural field is a pure function of coordinates and a seed. Same seed

**Functions:**

| Name | Signature | Docs |
|------|-----------|------|
| `procgen_seed` | `(s: u32) -> void` | — |
| `procgen_get_seed` | `() -> u32` | — |
| `procgen_hash` | `(ix: i32, iy: i32, iz: i32, salt: i32) -> u32` | Integer hash. Three rounds of xor-multiply, seeded from pg_seed0 so noise fields move with the module seed. |
| `procgen_noise3` | `(x: f32, y: f32, z: f32, salt: i32) -> f32` | Gradient noise in approximately [-1, 1]. |
| `procgen_noise2` | `(x: f32, y: f32, salt: i32) -> f32` | — |
| `procgen_fbm3` | `(x: f32, y: f32, z: f32, octaves: i32,
                             salt: i32) -> f32` | Fractional Brownian motion: octaves of gradient noise at doubling frequency and halving amplitude, normalised to roughly [-1, 1]. |
| `procgen_fbm2` | `(x: f32, y: f32, octaves: i32, salt: i32) -> f32` | — |
| `procgen_ridged3` | `(x: f32, y: f32, z: f32, octaves: i32,
                                salt: i32) -> f32` | Ridged multifractal: 1 - \|noise\| per octave, which turns the zero crossings into creases. Range [0, 1]. |
| `procgen_ridged2` | `(x: f32, y: f32, octaves: i32, salt: i32) -> f32` | — |
| `procgen_warped3` | `(x: f32, y: f32, z: f32, octaves: i32, warp: f32,
                                salt: i32) -> f32` | Domain-warped fBm: the sample point is displaced by another noise field first, which breaks the axis-aligned look of plain fBm. |
| `procgen_warped2` | `(x: f32, y: f32, octaves: i32, warp: f32,
                                salt: i32) -> f32` | — |
| `procgen_value2` | `(x: f32, y: f32, salt: i32) -> f32` | Value noise in [0, 1]. Hashes the integer lattice and interpolates the four corner values with a smoothstep weight, matching examples/threed/heightmap_terrain. |

### `psychstats.flow`

psychstats: the analysis half of Flow's behavioural-experiment support.  Everything a reaction-time or psychophysics paper reports, computed in Flow

**Structs:** `PsTTest`, `PsAnovaTerm`, `PsAnova2`, `PsTrim`, `PsLogNormal`, `PsFit`, `PsBootCI`, `PsSdt`

**Constants:**

- `PS_LOGISTIC: i32`
- `PS_WEIBULL: i32`

**Functions:**

| Name | Signature | Docs |
|------|-----------|------|
| `ps_seed` | `(seed: u32) -> u32` | — |
| `ps_seed_of_record` | `() -> u32` | The seed the last ps_seed call actually installed. Log it beside the data. |
| `ps_rand` | `() -> f64` | Uniform f64 in [0, 1). |
| `ps_rand_int` | `(n: i32) -> i32` | Uniform integer in [0, n). n <= 0 returns 0. |
| `ps_rand_normal` | `() -> f64` | — |
| `ps_rand_binomial` | `(m: i32, p: f64) -> i32` | Number of successes in m Bernoulli(p) draws. m is a trial count, so the direct loop is both exact and cheap. |
| `ps_sum` | `(x: ptr<f64>, n: i32) -> f64` | Descriptives |
| `ps_mean` | `(x: ptr<f64>, n: i32) -> f64` | — |
| `ps_var` | `(x: ptr<f64>, n: i32) -> f64` | Sample variance, denominator n - 1. |
| `ps_sd` | `(x: ptr<f64>, n: i32) -> f64` | — |
| `ps_sem` | `(x: ptr<f64>, n: i32) -> f64` | — |
| `ps_min` | `(x: ptr<f64>, n: i32) -> f64` | — |
| `ps_max` | `(x: ptr<f64>, n: i32) -> f64` | — |
| `ps_sort_into` | `(src: ptr<f64>, n: i32, dst: ptr<f64>) -> void` | Insertion sort of src[0..n) into dst. dst may alias nothing in src. |
| `ps_quantile` | `(x: ptr<f64>, n: i32, q: f64) -> f64` | Linear-interpolation quantile on the sorted sample (numpy's default, method="linear"): position q*(n-1) in the order statistics. |
| `ps_median` | `(x: ptr<f64>, n: i32) -> f64` | — |
| `ps_gammp` | `(a: f64, x: f64) -> f64` | Regularized lower incomplete gamma P(a, x). |
| `ps_norm_cdf` | `(z: f64) -> f64` | Standard normal CDF. Phi(z) = 0.5 * (1 + sign(z) * P(1/2, z^2/2)). |
| `ps_norm_pdf` | `(z: f64) -> f64` | — |
| `ps_norm_inv` | `(p: f64) -> f64` | Standard normal quantile. Wichura, "Algorithm AS 241: The percentage points of the normal distribution", Applied Statistics 37:477-484 (1988), PPND16 branch. Maximum absolute error about 1e-16 for p in (0, 1). |
| `ps_betai` | `(a: f64, b: f64, x: f64) -> f64` | Regularized incomplete beta I_x(a, b). |
| `ps_t_p2` | `(t: f64, df: f64) -> f64` | Two-tailed p for Student's t with df degrees of freedom. |
| `ps_t_cdf` | `(t: f64, df: f64) -> f64` | CDF of Student's t. |
| `ps_f_sf` | `(f: f64, df1: f64, df2: f64) -> f64` | Upper tail of the F distribution, i.e. the ANOVA p-value. |
| `ps_ttest_paired` | `(x: ptr<f64>, y: ptr<f64>, n: i32) -> PsTTest` | Paired (within-subject) t-test on x - y. Cohen's d here is d_z = mean(diff) / sd(diff), the effect size that matches the paired test statistic (t = d_z * sqrt(n)). Report it as d_z, not as the between-subject d; the two differ whenever the pair correlation is not zero. |
| `ps_ttest_ind` | `(x: ptr<f64>, nx: i32, y: ptr<f64>, ny: i32) -> PsTTest` | Independent-samples t-test, equal variances assumed (Student's). Cohen's d is the pooled-SD version, (m1 - m2) / s_pooled. |
| `ps_anova_rm1` | `(data: ptr<f64>, n_subj: i32, k: i32) -> PsAnovaTerm` | One-way repeated-measures ANOVA. data is n_subj rows of k condition means, row-major: data[s * k + c]. Error term is the subject x condition interaction. |
| `ps_anova_rm2` | `(data: ptr<f64>, n_subj: i32, na: i32, nb: i32) -> PsAnova2` | Two-way repeated-measures ANOVA, both factors within subject. data is n_subj rows of (na * nb) cell means, row-major within a row: data[s * na * nb + ia * nb + ib]. Each effect gets its own subject-interaction error term, which is the |
| `ps_perm_paired` | `(x: ptr<f64>, y: ptr<f64>, n: i32, iters: i32, seed: u32) -> f64` | Sign-flip permutation test on paired data. Two-tailed p on the mean difference, with the observed arrangement included in the count: p = (1 + #{\|mean*\| >= \|mean_obs\|}) / (1 + iters) which keeps p strictly positive (Phipson & Smyth 2010). |
| `ps_perm_ind` | `(x: ptr<f64>, nx: i32, y: ptr<f64>, ny: i32,
                            iters: i32, seed: u32) -> f64` | Label-shuffling permutation test for two independent groups. |
| `ps_trim_sd` | `(x: ptr<f64>, n: i32, k: f64, out: ptr<f64>) -> PsTrim` | Drop trials more than k SDs from the mean; write survivors to out. The cut is computed once from the full sample (no iteration), which is what "2.5 SD trimming" means in the RT literature and what a reader will assume. |
| `ps_trim_abs` | `(x: ptr<f64>, n: i32, lo: f64, hi: f64, out: ptr<f64>) -> PsTrim` | Drop trials outside an absolute window, the usual 200 ms / 2000 ms cut. |
| `ps_ies` | `(mean_rt: f64, accuracy: f64) -> f64` | Inverse efficiency score: mean correct RT divided by proportion correct (Townsend & Ashby 1983). Undefined at zero accuracy; returns 0 there. |
| `ps_lognormal_fit` | `(x: ptr<f64>, n: i32) -> PsLogNormal` | Maximum-likelihood log-normal fit. For the log-normal the MLE is exactly the mean and (population) SD of the logs, so no search is needed. |
| `ps_psy_p` | `(kind: i32, s: f64, alpha: f64, beta: f64,
                         gamma: f64, lambda: f64) -> f64` | Predicted proportion correct at stimulus level s. logistic: gamma + (1 - gamma - lambda) / (1 + exp(-(s - alpha) / beta)) Weibull:  gamma + (1 - gamma - lambda) * (1 - exp(-(s / alpha)^beta)) alpha is the threshold parameter, beta the width (logistic) or shape |
| `ps_fit` | `(kind: i32, s: ptr<f64>, k: ptr<f64>, m: ptr<f64>, n: i32,
                       gamma: f64, lambda: f64) -> PsFit` | Maximum-likelihood fit of a psychometric function to binomial counts. s[i]  stimulus level of block i k[i]  number correct at that level m[i]  number of trials at that level |
| `ps_fit_logistic` | `(s: ptr<f64>, k: ptr<f64>, m: ptr<f64>, n: i32,
                                gamma: f64, lambda: f64) -> PsFit` | — |
| `ps_fit_weibull` | `(s: ptr<f64>, k: ptr<f64>, m: ptr<f64>, n: i32,
                               gamma: f64, lambda: f64) -> PsFit` | — |
| `ps_fit_boot_ci` | `(kind: i32, s: ptr<f64>, k: ptr<f64>, m: ptr<f64>, n: i32,
                               gamma: f64, lambda: f64,
                               iters: i32, level: f64, seed: u32) -> PsBootCI` | Parametric bootstrap CI on the threshold: resample each level's correct count from Binomial(m[i], p_hat(s[i])) at the fitted parameters, refit, and take the empirical percentile interval. `level` is the two-sided coverage, so 0.95 gives the 2.5th and 97.5th percentiles. |
| `ps_sdt` | `(hits: i32, misses: i32, fas: i32, crs: i32) -> PsSdt` | d-prime and criterion from a 2x2 confusion table. Rates of exactly 0 or 1 make z infinite, so the log-linear correction of Hautus (1995) is applied to the whole table when that happens: add 0.5 to every cell and 1 to both totals. `corrected` says whether it fired. |
| `ps_auc` | `(signal: ptr<f64>, n1: i32, noise: ptr<f64>, n2: i32) -> f64` | Area under the ROC by the Mann-Whitney statistic: the probability that a random signal trial outranks a random noise trial, ties counting a half. Exact, and O(n1 * n2), which is nothing at experiment sizes. |
| `ps_auc_from_dprime` | `(d: f64) -> f64` | The equal-variance Gaussian relationship between d-prime and ROC area. |
| `ps_dprime_from_auc` | `(a: f64) -> f64` | — |

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

### `render3d.flow`

render3d: a software 3D renderer written in Flow.  Everything below runs on the CPU. There is no GPU, no driver, and no shader

**Functions:**

| Name | Signature | Docs |
|------|-----------|------|
| `r3d_clampf` | `(v: f32, lo: f32, hi: f32) -> f32` | Scalar helpers |
| `r3d_minf` | `(a: f32, b: f32) -> f32` | — |
| `r3d_maxf` | `(a: f32, b: f32) -> f32` | — |
| `r3d_lerpf` | `(a: f32, b: f32, t: f32) -> f32` | — |
| `r3d_radians` | `(deg: f32) -> f32` | — |
| `v3` | `(x: f32, y: f32, z: f32) -> V3` | Vector math |
| `v3_add` | `(a: V3, b: V3) -> V3` | — |
| `v3_sub` | `(a: V3, b: V3) -> V3` | — |
| `v3_mul` | `(a: V3, b: V3) -> V3` | — |
| `v3_scale` | `(a: V3, s: f32) -> V3` | — |
| `v3_neg` | `(a: V3) -> V3` | — |
| `v3_dot` | `(a: V3, b: V3) -> f32` | — |
| `v3_cross` | `(a: V3, b: V3) -> V3` | — |
| `v3_len` | `(a: V3) -> f32` | — |
| `v3_len2` | `(a: V3) -> f32` | — |
| `v3_dist` | `(a: V3, b: V3) -> f32` | — |
| `v3_norm` | `(a: V3) -> V3` | Zero-length input returns (0, 0, 0) rather than a NaN. |
| `v3_lerp` | `(a: V3, b: V3, t: f32) -> V3` | — |
| `v3_face_normal` | `(a: V3, b: V3, c: V3) -> V3` | Normal of the triangle a-b-c under counter-clockwise winding. |
| `m4_identity` | `(out: ptr<f32>) -> void` | 4x4 matrices, row-major, applied to column vectors |
| `m4_translation` | `(out: ptr<f32>, x: f32, y: f32, z: f32) -> void` | — |
| `m4_scaling` | `(out: ptr<f32>, sx: f32, sy: f32, sz: f32) -> void` | — |
| `m4_rotation_x` | `(out: ptr<f32>, a: f32) -> void` | — |
| `m4_rotation_y` | `(out: ptr<f32>, a: f32) -> void` | — |
| `m4_rotation_z` | `(out: ptr<f32>, a: f32) -> void` | — |
| `m4_mul` | `(out: ptr<f32>, a: &[f32], b: &[f32]) -> void` | out = a * b. `out` must not alias `a` or `b`. |
| `m4_copy` | `(out: ptr<f32>, src: &[f32]) -> void` | — |
| `m4_perspective` | `(out: ptr<f32>, fovy: f32, aspect: f32,
                               znear: f32, zfar: f32) -> void` | OpenGL-style perspective. fovy is the vertical field of view in radians. clip.w comes out equal to the view-space distance in front of the eye. |
| `m4_look_at` | `(out: ptr<f32>, eye: V3, target: V3, up: V3) -> void` | Right-handed look-at. `up` need not be perpendicular to the view direction. |
| `m4_point` | `(m: &[f32], p: V3) -> V3` | Transform a position (w = 1) and drop the resulting w. |
| `m4_dir` | `(m: &[f32], d: V3) -> V3` | Transform a direction (w = 0): the translation column is ignored. |
| `m4_pointw` | `(m: &[f32], p: V3) -> f32` | The w component of m * (p, 1); needed on its own for clip-space work. |
| `r3d_set_ambient` | `(a: f32) -> void` | Lighting |
| `r3d_ambient_level` | `() -> f32` | — |
| `r3d_lambert` | `(base: V3, normal: V3, to_light: V3) -> V3` | Lambert against a directional light. `to_light` points from the surface towards the light and is normalized here. The ambient term keeps unlit faces visible instead of black. |
| `r3d_set_fog` | `(on: bool, col: V3, start: f32, stop: f32) -> void` | Fog |
| `r3d_apply_fog` | `(col: V3, view_depth: f32) -> V3` | Linear fog on view depth. Returns the colour unchanged when fog is off. |
| `r3d_init` | `(w: i32, h: i32) -> bool` | Allocate every buffer once. Returns false if the resolution exceeds the fixed maximums or if any allocation fails. |
| `r3d_width` | `() -> i32` | — |
| `r3d_height` | `() -> i32` | — |
| `r3d_aspect` | `() -> f32` | — |
| `r3d_pixels` | `() -> ptr<u8>` | — |
| `r3d_set_cull` | `(mode: i32) -> void` | — |
| `r3d_set_near` | `(w: f32) -> void` | — |
| `r3d_clear` | `(col: V3) -> void` | Clear colour and depth, and reset the per-frame counters. |
| `r3d_clear_gradient` | `(top: V3, bottom: V3) -> void` | A vertical gradient background, cleared depth included. Cheaper than a sky mesh and it makes the horizon readable in the outdoor demos. |
| `r3d_put` | `(x: i32, y: i32, col: V3) -> void` | Write one pixel with no depth test. |
| `r3d_put_depth` | `(x: i32, y: i32, z: f32, col: V3) -> void` | Write one pixel if it passes and updates the depth test. |
| `r3d_depth_at` | `(x: i32, y: i32) -> f32` | Read the depth buffer, for tests and for depth-aware effects. |
| `r3d_present` | `(g: Gfx) -> void` | Blit the colour buffer into the window in one call. |
| `r3d_tris_submitted` | `() -> i32` | Statistics and timing |
| `r3d_tris_drawn` | `() -> i32` | — |
| `r3d_tris_clipped` | `() -> i32` | — |
| `r3d_tris_culled` | `() -> i32` | — |
| `r3d_pixels_shaded` | `() -> i32` | — |
| `r3d_tick` | `() -> void` | Call once per frame. Measures process CPU time between calls and keeps an exponential moving average, so the HUD number is the cost of the frame on the machine that is running it rather than a nominal target. |
| `r3d_fps` | `() -> f32` | — |
| `r3d_frame_ms` | `() -> f32` | — |
| `r3d_mesh_reset` | `() -> void` | Mesh building |
| `r3d_mesh_verts` | `() -> i32` | — |
| `r3d_mesh_tris` | `() -> i32` | — |
| `r3d_mesh_vertex` | `(p: V3, n: V3, c: V3) -> i32` | Append a vertex. Returns its index, or -1 when the capacity is exhausted. |
| `r3d_mesh_tri` | `(i0: i32, i1: i32, i2: i32) -> bool` | Append a triangle by vertex index. Counter-clockwise is front-facing. |
| `r3d_mesh_quad` | `(a: V3, b: V3, c: V3, d: V3, col: V3) -> void` | A flat quad a-b-c-d, wound counter-clockwise, with one shared normal. |
| `r3d_mesh_box` | `(centre: V3, half: V3, col: V3) -> void` | An axis-aligned box given its centre and half-extents. Six quads, each with its own normal, so the faces shade separately. |
| `r3d_mesh_box_face` | `(centre: V3, half: V3, face: i32, col: V3) -> void` | One box face by index: 0 +Z, 1 -Z, 2 +X, 3 -X, 4 +Y, 5 -Y. Voxel worlds need faces one at a time so hidden ones can be skipped. |
| `r3d_mesh_sphere` | `(centre: V3, radius: f32, segs: i32, rings: i32,
                                col: V3) -> void` | A UV sphere. `segs` divisions around, `rings` divisions top to bottom. Normals are exact, so this is the mesh to use for Gouraud shading. |
| `r3d_raster_tri` | `(a: SVert, b: SVert, c: SVert) -> void` | Fill one screen-space triangle with a depth test, back/front culling and perspective-correct colour. Coordinates are pixels, z is in [0, 1], iw is 1 / w_clip. |
| `r3d_clip_and_raster` | `(a: V4C, b: V4C, c: V4C) -> void` | Sutherland-Hodgman against w >= r3d_near, then fan-triangulate and raster. Everything in front of the eye survives untouched; a triangle straddling the plane becomes one or two triangles; one entirely behind disappears. |
| `r3d_tri` | `(viewproj: &[f32], pa: V3, pb: V3, pc: V3,
                       ca: V3, cb: V3, cc: V3) -> void` | Immediate-mode triangle: three world positions, three colours, one matrix. |
| `r3d_line` | `(x0: i32, y0: i32, x1: i32, y1: i32, col: V3) -> void` | Bresenham in screen space, no depth test. |
| `r3d_line_depth` | `(x0: i32, y0: i32, z0: f32,
                               x1: i32, y1: i32, z1: f32, col: V3) -> void` | Bresenham with a depth test, interpolating z linearly between the endpoints. |
| `r3d_line_clip` | `(a: V4C, b: V4C, col: V3) -> void` | A clip-space line segment, clipped to the near plane and depth-tested. This is the entry point the wireframe path uses, because the mesh vertices are already in clip space by then and re-transforming them per edge would triple the matrix work. |
| `r3d_line3` | `(viewproj: &[f32], pa: V3, pb: V3, col: V3) -> void` | A world-space line segment, clipped to the near plane and depth-tested. |
| `r3d_sprite` | `(viewproj: &[f32], centre: V3, radius: f32, col: V3) -> void` | A screen-aligned depth-tested disc at a world point, sized by `radius` in world units at the point's distance. This is the billboard primitive: it always faces the camera because it is drawn in screen space. |
| `r3d_sprite_blend` | `(viewproj: &[f32], centre: V3, radius: f32,
                                 col: V3, alpha: f32) -> i32` | Alpha-blended billboard. The depth buffer is read but never written, so a translucent sprite is hidden by solid geometry in front of it without occluding the sprites behind it. That makes the result order-dependent: the caller must submit these back to front. Returns the number of pixels touched. |
| `r3d_draw_mesh` | `(model: &[f32], viewproj: &[f32], to_light: V3,
                              mode: i32) -> void` | Transform, light, clip and rasterize the whole current mesh. model     object to world viewproj  world to clip to_light  direction from a surface towards the directional light |
| `r3d_ray_aabb` | `(origin: V3, dir: V3, lo: V3, hi: V3) -> f32` | Slab test against an axis-aligned box. Returns the entry distance along the ray, or -1.0 when there is no hit in front of the origin. |
| `r3d_ray_sphere` | `(origin: V3, dir: V3, centre: V3, radius: f32) -> f32` | Nearest intersection of a ray with a sphere, or -1.0 for a miss. |
| `r3d_forward` | `(yaw: f32, pitch: f32) -> V3` | The view direction for a camera given yaw (around +Y, 0 looks down -Z) and pitch (positive looks up). |
| … | 1 more | |

### `result.flow`

Result Type Represents either success (Ok(value)) or failure (Err(error))

*No `export` items found (internal / extern-only module).*

### `rf.flow`

RF / SDR Module - IQ Samples and Rate-Typed Signals  Complex baseband processing primitives for software-defined radio.

**Functions:**

| Name | Signature | Docs |
|------|-----------|------|
| `iq` | `(re: f32, im: f32) -> IQ` | IQ constructors |
| `iq_from_real` | `(re: f32) -> IQ` | — |
| `iq_sample` | `(re: f32, im: f32) -> IQSample` | — |
| `iq_sample_from_iq` | `(z: IQ) -> IQSample` | — |

### `sdl2.flow`

SDL2 bindings (minimal)  This is a deliberately tiny subset needed for simple 2D apps.

*No `export` items found (internal / extern-only module).*

### `slice.flow`

FLOW Slice Type A slice is a view into a contiguous block of memory (ptr + length)

*No `export` items found (internal / extern-only module).*

### `sorting/core.flow`

Sorting library: shared core.  Everything the algorithm modules need in common: the element swap, the

**Constants:**

- `SORT_SCRATCH_CAPACITY: i64`
- `SORT_TAG_CAPACITY: i64`
- `SORT_COUNT_CAPACITY: i64`
- `SORT_INSERTION_CUTOFF: i64`

**Functions:**

| Name | Signature | Docs |
|------|-----------|------|
| `sort_scratch` | `(n: i64) -> span<mut i32>` | A mutable view of the first `n` elements of the merge scratch. Returns a zero-length span when `n` exceeds the documented capacity, which every caller checks before relying on it. |
| `sort_tags` | `(n: i64) -> span<mut i32>` | A mutable view of the first `n` elements of the tag scratch. |
| `sort_counts` | `(k: i64) -> span<mut i32>` | A mutable view of the first `k` histogram slots, zeroed. |
| `sort_swap` | `(xs: &mut [i32], i: i64, j: i64) -> void` | — |
| `sort_reverse` | `(xs: &mut [i32]) -> void` | Reverse in place. Used by the descending wrappers and by the adversarial input generators in the test harness. |
| `sort_copy` | `(dst: &mut [i32], src: &[i32]) -> void` | Copy `src` over `dst`, element for element. Both are spans, so the lengths travel with the data and the shorter one bounds the copy. |
| `is_sorted` | `(xs: &[i32]) -> bool` | True when `xs` is in non-decreasing order. O(n), no allocation. |
| `is_sorted_descending` | `(xs: &[i32]) -> bool` | True when `xs` is in non-increasing order. |
| `is_strictly_increasing` | `(xs: &[i32]) -> bool` | True when `xs` is strictly increasing (no duplicates). |
| `is_sorted_by` | `(xs: &[i32], le: (i32, i32) -> bool) -> bool` | True when every adjacent pair satisfies `le`. The comparator is a first-class `(i32, i32) -> bool`. One caller-side note: a lambda written directly at the call site is not wrapped into the closure struct by the current C backend, so bind it to an annotated local first: |
| `spans_equal` | `(a: &[i32], b: &[i32]) -> bool` | Do two spans hold the same elements in the same order? |
| `span_min` | `(xs: &[i32]) -> i32` | Smallest and largest element. Returns 0 for an empty span; callers that care check `.len` first. |
| `span_max` | `(xs: &[i32]) -> i32` | — |
| `rng_seed` | `(seed: i64) -> void` | — |
| `rng_next` | `() -> i32` | Next value in [0, 2^31 - 1). |
| `rng_below` | `(bound: i32) -> i32` | Next value in [0, bound). Returns 0 for a non-positive bound. |
| `shuffle` | `(xs: &mut [i32]) -> void` | Fisher-Yates over a span, drawing from the LCG above. |
| `ord_key_f64` | `(x: f64) -> i64` | — |
| `ord_cmp_f64` | `(a: f64, b: f64) -> i32` | — |
| `is_sorted_total_f64` | `(xs: &[f64]) -> bool` | True when `xs` is in non-decreasing totalOrder. Unlike a check built from `<=`, this is correct in the presence of NaN and signed zero. |

### `sorting/gapped.flow`

Sorting library: gap sequence sorts.  Shell sort and comb sort are the same idea applied to two different

**Functions:**

| Name | Signature | Docs |
|------|-----------|------|
| `shell_sort` | `(xs: &mut [i32]) -> void` | — |
| `comb_sort` | `(xs: &mut [i32]) -> void` | comb_sort NOT stable best O(n log n)   average ~O(n^2 / 2^p) empirically near O(n log n) worst O(n^2)      extra space O(1) |

### `sorting/heap.flow`

Sorting library: the heap family.  A binary max-heap laid out in the span itself: the children of `i` live at

**Constants:**

- `TOURNAMENT_CAPACITY: i64`

**Functions:**

| Name | Signature | Docs |
|------|-----------|------|
| `heapify` | `(xs: &mut [i32]) -> void` | Turn a span into a max-heap. Floyd's bottom-up construction: O(n), not O(n log n), because most nodes are near the leaves and sift down barely at all. |
| `heap_sort` | `(xs: &mut [i32]) -> void` | heap_sort NOT stable (the root/last swap reorders equal keys arbitrarily) best O(n log n)   average O(n log n)   worst O(n log n) extra space O(1) |
| `partial_sort` | `(xs: &mut [i32], k: i64) -> void` | partial_sort NOT stable O(n + k log n) with a full heapify, or O(n log k) via the bounded heap below, whichever the caller asks for. |
| `top_k_descending` | `(xs: &mut [i32], k: i64) -> void` | top_k_descending NOT stable O(n log k)   extra space O(1) Leaves the k largest elements in `xs[0..k]`, largest first. Same machinery |
| `tournament_sort` | `(xs: &mut [i32]) -> void` | — |

### `sorting/merge.flow`

Sorting library: the merge family.  Four ways to spend O(n) scratch to buy stability and an n log n worst case.

**Functions:**

| Name | Signature | Docs |
|------|-----------|------|
| `merge_sort` | `(xs: &mut [i32]) -> void` | merge_sort (top-down) stable best O(n log n)   average O(n log n)   worst O(n log n) extra space O(n) from the shared scratch pool |
| `bottom_up_merge_sort` | `(xs: &mut [i32]) -> void` | bottom_up_merge_sort stable best O(n log n)   average O(n log n)   worst O(n log n) extra space O(n) |
| `natural_merge_sort` | `(xs: &mut [i32]) -> void` | natural_merge_sort stable best O(n) on an input that is already one run average O(n log r) where r is the number of runs |
| `tim_sort` | `(xs: &mut [i32]) -> void` | — |

### `sorting/quadratic.flow`

Sorting library: the quadratic family.  Six algorithms that all do O(n^2) work in the general case. Two of them

**Functions:**

| Name | Signature | Docs |
|------|-----------|------|
| `insertion_sort` | `(xs: &mut [i32]) -> void` | insertion_sort stable best O(n)   average O(n^2)   worst O(n^2)   extra space O(1) Pick it when: n is under ~32, or the input is nearly ordered. It is the |
| `binary_insertion_sort` | `(xs: &mut [i32]) -> void` | binary_insertion_sort stable best O(n log n) comparisons / O(n) moves average O(n^2) moves   worst O(n^2) moves   extra space O(1) |
| `selection_sort` | `(xs: &mut [i32]) -> void` | selection_sort NOT stable (the long-range swap jumps an equal element over its peers) best O(n^2)   average O(n^2)   worst O(n^2)   extra space O(1) moves: exactly n - 1 swaps, which is its one virtue. |
| `double_selection_sort` | `(xs: &mut [i32]) -> void` | double_selection_sort NOT stable best O(n^2)   average O(n^2)   worst O(n^2)   extra space O(1) Finds the minimum and the maximum in one pass, so it halves the number of |
| `bubble_sort` | `(xs: &mut [i32]) -> void` | bubble_sort stable best O(n) with the early-exit flag   average O(n^2)   worst O(n^2) extra space O(1) |
| `cocktail_shaker_sort` | `(xs: &mut [i32]) -> void` | cocktail_shaker_sort stable best O(n)   average O(n^2)   worst O(n^2)   extra space O(1) Bubble sort that alternates direction. It fixes bubble sort's one |
| `gnome_sort` | `(xs: &mut [i32]) -> void` | gnome_sort stable best O(n)   average O(n^2)   worst O(n^2)   extra space O(1) Insertion sort written as a single loop with one index that walks |
| `odd_even_sort` | `(xs: &mut [i32]) -> void` | odd_even_sort (brick sort) stable best O(n)   average O(n^2)   worst O(n^2)   extra space O(1) A bubble sort split into two independent phases. Every compare-exchange |

### `sorting/quick.flow`

Sorting library: the partitioning family.  Quicksort and its relatives. Everything here recurses by *slicing the span*:

**Functions:**

| Name | Signature | Docs |
|------|-----------|------|
| `quick_sort` | `(xs: &mut [i32]) -> void` | quick_sort NOT stable best O(n log n)   average O(n log n)   worst O(n^2) extra space O(log n) stack, from the recursion on the smaller half only |
| `dual_pivot_quick_sort` | `(xs: &mut [i32]) -> void` | dual_pivot_quick_sort NOT stable best O(n log n)   average O(n log n)   worst O(n^2) extra space O(log n) stack |
| `intro_sort` | `(xs: &mut [i32]) -> void` | intro_sort NOT stable best O(n log n)   average O(n log n)   worst O(n log n) extra space O(log n) stack |
| `random_pivot_quick_sort` | `(xs: &mut [i32]) -> void` | random_pivot_quick_sort NOT stable best O(n log n)   average O(n log n) expected   worst O(n^2) with probability that vanishes in n |
| `quickselect` | `(xs: &mut [i32], k: i64) -> i32` | quickselect NOT stable, and it permutes the input best O(n)   average O(n)   worst O(n^2) extra space O(1) — the recursion is eliminated entirely |
| `median` | `(xs: &mut [i32]) -> i32` | The median. For an even length this is the lower of the two middle values, which is the convention that needs no arithmetic on the elements and so works for any orderable type. |
| `three_way_quick_sort` | `(xs: &mut [i32]) -> void` | three_way_quick_sort (Dutch national flag) NOT stable best O(n)   average O(n log n)   worst O(n^2) extra space O(log n) stack |

### `spice.flow`

SPICE NETLIST FRONT END: a subset parser that builds stdlib/circuit.flow structures.

**Functions:**

| Name | Signature | Docs |
|------|-----------|------|
| `spice_node` | `(name: string) -> i32` | Look up a node by name from outside the parser. |
| `spice_node_count` | `() -> i32` | — |
| `spice_source` | `(name: string) -> i32` | Element index of a named source, or -1. |
| `spice_load` | `(path: string) -> bool` | Read a deck from disk. Returns false if the file is missing or larger than SPICE_MAX_TEXT. |
| `spice_parse` | `() -> bool` | Parse the loaded deck into stdlib/circuit.flow, then finalize it. The first non-blank line is the title, as SPICE requires. |
| `spice_error_line` | `() -> i32` | — |
| `spice_skipped` | `() -> i32` | — |
| `spice_has_tran` | `() -> bool` | — |
| `spice_tstep` | `() -> f64` | — |
| `spice_tstop` | `() -> f64` | — |
| `spice_uic` | `() -> bool` | — |
| `spice_has_dc` | `() -> bool` | — |
| `spice_dc_source` | `() -> i32` | — |
| `spice_dc_start` | `() -> f64` | — |
| `spice_dc_stop` | `() -> f64` | — |
| `spice_dc_step` | `() -> f64` | — |
| `spice_has_op` | `() -> bool` | — |

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
| `ui_layout_unit` | `(state: ptr<UiLayoutState>) -> f32` | — |

### `units_si.flow`

SI Units Module - Base dimensions and SI-prefixed units  Provides base SI dimensions and common derived units with SI prefixes.

*No `export` items found (internal / extern-only module).*

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

