# Standard Library API (generated)

> Auto-generated from `lib/stdlib/` on 2026-08-05 by `scripts/gen_stdlib_docs.py`. Hand-written guides live alongside this page.

**82** modules scanned.

## Modules

### `array.flow`

Sum the first `size` elements of an f32 array.

**Functions:**

| Name | Signature |
|------|-----------|
| `sum` | `(arr: array<f32>, size: i32) -> f32` |

### `async.flow`

Async primitives via algebraic effects  Call sites perform `Async` / `AsyncIO` operations; a capability supplies the

**Functions:**

| Name | Signature |
|------|-----------|
| `async_delay` | `(ms: i32) -> void` |
| `async_spawn` | `(task_id: i32) -> void` |
| `async_join` | `(task_id: i32) -> i32` |
| `async_sleep_ms` | `(ms: i32) -> void` |
| `async_poll_read` | `(fd: i32, timeout_ms: i32) -> i32` |

### `audio/clock.flow`

Audio Clock Module - BPM, Tempo, and Timing  Makes rhythm and timing incredibly easy with BPM-based scheduling.

**Structs:** `Clock`, `TimeSignature`, `SwingClock`

**Functions:**

| Name | Signature |
|------|-----------|
| `clock_new` | `(bpm: f64, rate: SampleRate) -> Clock` |
| `clock_new_with_sig` | `(bpm: f64, rate: SampleRate, sig: TimeSignature) -> Clock` |
| `clock_slow` | `(rate: SampleRate) -> Clock` |
| `clock_medium` | `(rate: SampleRate) -> Clock` |
| `clock_fast` | `(rate: SampleRate) -> Clock` |
| `clock_house` | `(rate: SampleRate) -> Clock` |
| `clock_dnb` | `(rate: SampleRate) -> Clock` |
| `clock_techno` | `(rate: SampleRate) -> Clock` |
| `time_sig_4_4` | `() -> TimeSignature` |
| `time_sig_3_4` | `() -> TimeSignature` |
| `time_sig_6_8` | `() -> TimeSignature` |
| `time_sig_5_4` | `() -> TimeSignature` |
| `time_sig_7_8` | `() -> TimeSignature` |
| `samples_per_beat` | `(clock: Clock) -> i64` |
| `samples_per_bar` | `(clock: Clock) -> i64` |
| `samples_per_measure` | `(clock: Clock) -> i64` |
| `samples_per_whole` | `(clock: Clock) -> i64` |
| `samples_per_half` | `(clock: Clock) -> i64` |
| `samples_per_quarter` | `(clock: Clock) -> i64` |
| `samples_per_eighth` | `(clock: Clock) -> i64` |
| `samples_per_sixteenth` | `(clock: Clock) -> i64` |
| `samples_per_thirtysecond` | `(clock: Clock) -> i64` |
| `samples_per_quarter_dotted` | `(clock: Clock) -> i64` |
| `samples_per_quarter_triplet` | `(clock: Clock) -> i64` |
| `clock_on_beat` | `(clock: Clock, sample_pos: i64) -> bool` |
| `clock_on_bar` | `(clock: Clock, sample_pos: i64) -> bool` |
| `clock_on_sixteenth` | `(clock: Clock, sample_pos: i64) -> bool` |
| `clock_current_beat` | `(clock: Clock, sample_pos: i64) -> i64` |
| `clock_current_bar` | `(clock: Clock, sample_pos: i64) -> i64` |
| `clock_beat_in_bar` | `(clock: Clock, sample_pos: i64) -> i32` |
| `clock_sixteenth_in_beat` | `(clock: Clock, sample_pos: i64) -> i32` |
| `clock_set_bpm` | `(clock: Clock, new_bpm: f64) -> Clock` |
| `clock_scale_tempo` | `(clock: Clock, factor: f64) -> Clock` |
| `clock_double_tempo` | `(clock: Clock) -> Clock` |
| `clock_half_tempo` | `(clock: Clock) -> Clock` |
| `swing_clock_new` | `(bpm: f64, rate: SampleRate, swing: f64) -> SwingClock` |
| `swing_position` | `(sclock: SwingClock, sixteenth: i32) -> f64` |
| `bpm_to_hz` | `(bpm: f64) -> f64` |
| `hz_to_bpm` | `(hz: f64) -> f64` |
| `ms_per_beat` | `(clock: Clock) -> f64` |
| `beats_per_second` | `(clock: Clock) -> f64` |
| `delay_time_samples` | `(clock: Clock, note_value: f64) -> i64` |
| `dotted` | `(note_value: f64) -> f64` |
| `triplet` | `(note_value: f64) -> f64` |

### `audio/control.flow`

Audio Control Utilities  Control-rate smoothing and parameter utilities.

**Structs:** `ParamSmoother`

**Functions:**

| Name | Signature |
|------|-----------|
| `param_smoother_new` | `(initial: f32, time_ms: f32, rate: SampleRate) -> ParamSmoother` |
| `param_smoother_set_target` | `(p: ParamSmoother, target: f32) -> ParamSmoother` |
| `param_smoother_tick` | `(p: ParamSmoother) -> ParamSmoother` |
| `param_smoother_value` | `(p: ParamSmoother) -> f32` |

### `audio/delay.flow`

Audio Delay Module  Delay lines and time-based effects.

**Structs:** `DelayState`, `PingPongState`, `AllpassDelay`, `CombFilter`, `ModDelay`

**Functions:**

| Name | Signature |
|------|-----------|
| `delay_new` | `(max_time: Seconds, rate: SampleRate) -> DelayState` |
| `delay_set_time` | `(d: DelayState, time: Seconds, rate: SampleRate) -> DelayState` |
| `delay_set_feedback` | `(d: DelayState, fb: f32) -> DelayState` |
| `delay_set_mix` | `(d: DelayState, mix: f32) -> DelayState` |
| `delay_advance` | `(d: DelayState) -> DelayState` |
| `delay_read_pos` | `(d: DelayState) -> i64` |
| `pingpong_new` | `(time: Seconds, rate: SampleRate) -> PingPongState` |
| `pingpong_set_feedback` | `(pp: PingPongState, fb: f32) -> PingPongState` |
| `lerp` | `(a: f32, b: f32, t: f32) -> f32` |
| `cubic_interp` | `(y0: f32, y1: f32, y2: f32, y3: f32, t: f32) -> f32` |
| `allpass_delay_new` | `(time_ms: f32, coeff: f32, rate: SampleRate) -> AllpassDelay` |
| `allpass_delay_advance` | `(a: AllpassDelay) -> AllpassDelay` |
| `comb_new` | `(time_ms: f32, feedback: f32, damping: f32, rate: SampleRate) -> CombFilter` |
| `comb_advance` | `(c: CombFilter) -> CombFilter` |
| `mod_delay_new` | `(base_time: Seconds, mod_depth_ms: f32, mod_rate: f32, rate: SampleRate) -> ModDelay` |
| `mod_delay_tick` | `(m: ModDelay) -> ModDelay` |
| `mod_delay_current_samples` | `(m: ModDelay) -> f32` |
| `mod_delay_set_rate` | `(m: ModDelay, rate_hz: f32, sample_rate: SampleRate) -> ModDelay` |
| `mod_delay_set_depth` | `(m: ModDelay, depth_ms: f32, rate: SampleRate) -> ModDelay` |

### `audio/delay_line.flow`

Delay Line (F32) with Real Buffer Storage  Uses AudioBufferF32 for a real ring buffer implementation.

**Structs:** `DelayLineF32`

**Functions:**

| Name | Signature |
|------|-----------|
| `delay_line_empty` | `() -> DelayLineF32` |
| `delay_line_new` | `(max_ms: f32, rate: SampleRate) -> DelayLineF32` |
| `delay_line_set_time` | `(d: DelayLineF32, time_ms: f32, rate: SampleRate) -> DelayLineF32` |
| `delay_line_set_feedback` | `(d: DelayLineF32, fb: f32) -> DelayLineF32` |
| `delay_line_set_mix` | `(d: DelayLineF32, mix: f32) -> DelayLineF32` |
| `delay_line_tick` | `(d: DelayLineF32, input: f32) -> DelayLineF32` |
| `delay_line_output` | `(d: DelayLineF32) -> f32` |
| `delay_line_reset` | `(d: DelayLineF32) -> DelayLineF32` |

### `audio/effects.flow`

Audio Effects Module - Common Effects Processors  Ready-to-use effects: reverb, delay, distortion, chorus, etc.

**Structs:** `Delay`, `Distortion`, `Chorus`, `Compressor`, `Bitcrusher`, `Reverb`

**Functions:**

| Name | Signature |
|------|-----------|
| `delay_new` | `(time_samples: i32, feedback: f32, mix: f32) -> Delay` |
| `delay_new_at_rate` | `(time_samples: i32, feedback: f32, mix: f32, rate: SampleRate) -> Delay` |
| `delay_quarter_note` | `(clock: Clock) -> Delay` |
| `delay_eighth_note` | `(clock: Clock) -> Delay` |
| `delay_dotted_eighth` | `(clock: Clock) -> Delay` |
| `delay_process` | `(delay: Delay, input: f32) -> f32` |
| `delay_tick` | `(delay: Delay, input: f32) -> Delay` |
| `delay_output` | `(delay: Delay) -> f32` |
| `distortion_new` | `(drive: f32, tone: f32, mix: f32) -> Distortion` |
| `distortion_light` | `() -> Distortion` |
| `distortion_medium` | `() -> Distortion` |
| `distortion_heavy` | `() -> Distortion` |
| `distortion_fuzz` | `() -> Distortion` |
| `distortion_process` | `(dist: Distortion, input: f32) -> f32` |
| `chorus_new` | `(rate: f32, depth: f32, mix: f32) -> Chorus` |
| `chorus_subtle` | `() -> Chorus` |
| `chorus_medium` | `() -> Chorus` |
| `chorus_wide` | `() -> Chorus` |
| `chorus_process` | `(chorus: Chorus, input: f32) -> f32` |
| `chorus_tick` | `(chorus: Chorus, input: f32) -> Chorus` |
| `compressor_new` | `(threshold: f32, ratio: f32, attack: f32, release: f32) -> Compressor` |
| `compressor_gentle` | `() -> Compressor` |
| `compressor_medium` | `() -> Compressor` |
| `compressor_hard` | `() -> Compressor` |
| `limiter` | `() -> Compressor` |
| `compressor_process` | `(comp: Compressor, input: f32) -> f32` |
| `bitcrusher_new` | `(bits: i32, sample_rate_div: i32) -> Bitcrusher` |
| `bitcrusher_lofi` | `() -> Bitcrusher` |
| `bitcrusher_telephone` | `() -> Bitcrusher` |
| `bitcrusher_crushed` | `() -> Bitcrusher` |
| `bitcrusher_process` | `(crusher: Bitcrusher, input: f32) -> f32` |
| `reverb_new` | `(room_size: f32, damping: f32, mix: f32) -> Reverb` |
| `reverb_small_room` | `() -> Reverb` |
| `reverb_medium_hall` | `() -> Reverb` |
| `reverb_large_hall` | `() -> Reverb` |
| `reverb_plate` | `() -> Reverb` |
| `reverb_process` | `(rev: Reverb, input: f32) -> f32` |

### `audio/envelopes.flow`

Audio Envelopes Module  Envelope generators for amplitude, filter, and modulation control.

**Structs:** `EnvStage`, `ADSR`, `AR`, `Ramp`, `ExpDecay`

**Functions:**

| Name | Signature |
|------|-----------|
| `stage_idle` | `() -> EnvStage` |
| `stage_attack` | `() -> EnvStage` |
| `stage_decay` | `() -> EnvStage` |
| `stage_sustain` | `() -> EnvStage` |
| `stage_release` | `() -> EnvStage` |
| `adsr_new` | `(attack: Seconds, decay: Seconds, sustain: f32, release: Seconds, rate: SampleRate) -> ADSR` |
| `adsr_new_ms` | `(attack_ms: f32, decay_ms: f32, sustain: f32, release_ms: f32, rate: SampleRate) -> ADSR` |
| `adsr_gate_on` | `(e: ADSR) -> ADSR` |
| `adsr_gate_off` | `(e: ADSR) -> ADSR` |
| `adsr_tick` | `(e: ADSR) -> ADSR` |
| `adsr_value` | `(e: ADSR) -> f32` |
| `adsr_is_active` | `(e: ADSR) -> bool` |
| `adsr_is_idle` | `(e: ADSR) -> bool` |
| `adsr_reset` | `(e: ADSR) -> ADSR` |
| `ar_new` | `(attack: Seconds, release: Seconds, rate: SampleRate) -> AR` |
| `ar_trigger` | `(e: AR) -> AR` |
| `ar_tick` | `(e: AR) -> AR` |
| `ar_value` | `(e: AR) -> f32` |
| `ar_is_active` | `(e: AR) -> bool` |
| `ramp_new` | `(start_val: f32, end_val: f32, duration: Seconds, rate: SampleRate) -> Ramp` |
| `ramp_start` | `(r: Ramp) -> Ramp` |
| `ramp_set_target` | `(r: Ramp, target: f32, duration: Seconds, rate: SampleRate) -> Ramp` |
| `ramp_tick` | `(r: Ramp) -> Ramp` |
| `ramp_value` | `(r: Ramp) -> f32` |
| `exp_decay_new` | `(time_constant_ms: f32, rate: SampleRate) -> ExpDecay` |
| `exp_decay_trigger` | `(e: ExpDecay) -> ExpDecay` |
| `exp_decay_tick` | `(e: ExpDecay) -> ExpDecay` |
| `exp_decay_value` | `(e: ExpDecay) -> f32` |

### `audio/filters.flow`

Audio Filters Module  Digital filters for audio processing.

**Structs:** `OnePole`, `DCBlocker`, `Biquad`, `SVF`

**Functions:**

| Name | Signature |
|------|-----------|
| `onepole_lowpass` | `(cutoff_hz: f32, rate: SampleRate) -> OnePole` |
| `onepole_smooth` | `(time_ms: f32, rate: SampleRate) -> OnePole` |
| `onepole_tick` | `(f: OnePole, input: f32) -> OnePole` |
| `onepole_output` | `(f: OnePole) -> f32` |
| `onepole_reset` | `(f: OnePole) -> OnePole` |
| `onepole_set_state` | `(f: OnePole, value: f32) -> OnePole` |
| `dcblocker_new` | `(rate: SampleRate) -> DCBlocker` |
| `dcblocker_tick` | `(dc: DCBlocker, input: f32) -> DCBlocker` |
| `dcblocker_output` | `(dc: DCBlocker) -> f32` |
| `biquad_bypass` | `() -> Biquad` |
| `biquad_lowpass` | `(cutoff: f32, q: f32, rate: SampleRate) -> Biquad` |
| `biquad_highpass` | `(cutoff: f32, q: f32, rate: SampleRate) -> Biquad` |
| `biquad_bandpass` | `(center: f32, q: f32, rate: SampleRate) -> Biquad` |
| `biquad_notch` | `(center: f32, q: f32, rate: SampleRate) -> Biquad` |
| `biquad_allpass` | `(center: f32, q: f32, rate: SampleRate) -> Biquad` |
| `biquad_tick` | `(f: Biquad, input: f32) -> Biquad` |
| `biquad_output` | `(f: Biquad) -> f32` |
| `biquad_process` | `(f: Biquad, input: f32) -> f32` |
| `biquad_reset` | `(f: Biquad) -> Biquad` |
| `biquad_set_cutoff` | `(f: Biquad, cutoff: f32, q: f32, rate: SampleRate) -> Biquad` |
| `svf_new` | `(cutoff: f32, q: f32, rate: SampleRate) -> SVF` |
| `svf_tick_lowpass` | `(f: SVF, input: f32) -> SVF` |
| `svf_lowpass` | `(f: SVF) -> f32` |
| `svf_highpass` | `(f: SVF, input: f32) -> f32` |
| `svf_bandpass` | `(f: SVF) -> f32` |
| `svf_reset` | `(f: SVF) -> SVF` |

### `audio/gpu.flow`

Audio GPU Acceleration (Scaffold)  This module defines a simple backend switch to allow CPU/GPU paths.

**Structs:** `AudioComputeBackend`

**Functions:**

| Name | Signature |
|------|-----------|
| `audio_backend_cpu` | `() -> AudioComputeBackend` |
| `audio_backend_gpu` | `() -> AudioComputeBackend` |
| `audio_backend_is_gpu` | `(b: AudioComputeBackend) -> bool` |
| `audio_backend_gpu_available` | `() -> bool` |
| `audio_gain_block` | `(b: AudioComputeBackend, buf: AudioBufferF32, gain: f32) -> void` |
| `audio_convolution_block` | `(b: AudioComputeBackend, input: AudioBufferF32, impulse: AudioBufferF32) -> void` |
| `audio_fft_block` | `(b: AudioComputeBackend, buf: AudioBufferF32) -> void` |

### `audio/graph.flow`

Audio Graph Helpers (High-Level)  Simple, pragmatic effect chains for real-time routing.

**Structs:** `EffectChain`

**Functions:**

| Name | Signature |
|------|-----------|
| `effect_chain_new` | `(rate: SampleRate) -> EffectChain` |
| `effect_chain_set_gain_db` | `(c: EffectChain, db: f32) -> EffectChain` |
| `effect_chain_set_pan` | `(c: EffectChain, pan: f32) -> EffectChain` |
| `effect_chain_enable_lowpass` | `(c: EffectChain, cutoff: f32, q: f32, rate: SampleRate) -> EffectChain` |
| `effect_chain_enable_delay` | `(c: EffectChain, time_ms: f32, feedback: f32, mix: f32, rate: SampleRate) -> EffectChain` |
| `effect_chain_update` | `(c: EffectChain,
                                    gain_db: f32,
                                    pan: f32,
                                    enable_lowpass: bool,
                                    cutoff: f32,
                                    enable_delay: bool,
                                    delay_ms: f32,
                                    feedback: f32,
                                    mix: f32) -> EffectChain` |
| `effect_chain_tick` | `(c: EffectChain, input: Frame) -> EffectChain` |
| `effect_chain_output` | `(c: EffectChain) -> Frame` |
| `effect_chain_process_interleaved` | `(c: EffectChain, buf: AudioBufferF32) -> EffectChain` |
| `effect_chain_process_interleaved_frames` | `(c: EffectChain, buf: AudioBufferF32, frames: i32) -> EffectChain` |

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

| Name | Signature |
|------|-----------|
| `bus_node_default` | `() -> BusNode` |
| `bus_graph_init` | `(rate: SampleRate, buses: array<AudioBus, 8>, nodes: array<BusNode, 64>, scratch: AudioBufferF32) -> BusGraph` |
| `bus_graph_free` | `(g: BusGraph) -> void` |
| `bus_graph_add_gain` | `(g: BusGraph, input_bus: i32, output_bus: i32, gain_db: f32) -> BusGraph` |
| `bus_graph_add_lowpass` | `(g: BusGraph, input_bus: i32, output_bus: i32, cutoff: f32, q: f32) -> BusGraph` |
| `bus_graph_add_delay` | `(g: BusGraph, input_bus: i32, output_bus: i32, delay_ms: f32, feedback: f32, mix: f32) -> BusGraph` |
| `bus_graph_add_pan` | `(g: BusGraph, input_bus: i32, output_bus: i32, pan: f32) -> BusGraph` |
| `bus_graph_clear_buses` | `(g: BusGraph) -> void` |
| `bus_graph_process` | `(g: BusGraph, frames: i32) -> BusGraph` |

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

| Name | Signature |
|------|-----------|
| `audio_node_default` | `() -> AudioNode` |
| `audio_graph_init` | `(rate: SampleRate, nodes: array<AudioNode, 32>) -> AudioGraph` |
| `audio_graph_add_gain` | `(g: AudioGraph, gain_db: f32) -> AudioGraph` |
| `audio_graph_add_lowpass` | `(g: AudioGraph, cutoff: f32, q: f32) -> AudioGraph` |
| `audio_graph_add_delay` | `(g: AudioGraph, delay_ms: f32, feedback: f32, mix: f32) -> AudioGraph` |
| `audio_graph_add_pan` | `(g: AudioGraph, pan: f32) -> AudioGraph` |
| `audio_graph_process_interleaved` | `(g: AudioGraph, buf: AudioBufferF32, frames: i32) -> AudioGraph` |

### `audio/io.flow`

Audio I/O Module (Real-Time)  Cross-platform audio I/O facade. Backend implemented in runtime (C).

**Structs:** `AudioDeviceConfig`, `AudioDevice`

**Constants:**

- `AUDIO_OK: i32`
- `AUDIO_ERR: i32`

**Functions:**

| Name | Signature |
|------|-----------|
| `audio_device_config` | `(sample_rate: i32, channels: i32, frames_per_buffer: i32,
                                    enable_input: bool, enable_output: bool) -> AudioDeviceConfig` |
| `audio_device_ok` | `(dev: AudioDevice) -> bool` |
| `audio_device_open` | `(config: AudioDeviceConfig) -> AudioDevice` |
| `audio_device_start` | `(dev: AudioDevice) -> i32` |
| `audio_device_stop` | `(dev: AudioDevice) -> i32` |
| `audio_device_close` | `(dev: AudioDevice) -> void` |
| `audio_read_f32` | `(dev: AudioDevice, out: ptr<f32>, frames: i32) -> i32` |
| `audio_write_f32` | `(dev: AudioDevice, input: ptr<f32>, frames: i32) -> i32` |
| `audio_available_read` | `(dev: AudioDevice) -> i32` |
| `audio_available_write` | `(dev: AudioDevice) -> i32` |
| `audio_last_error` | `(dev: AudioDevice) -> string` |
| `audio_probe_devices` | `() -> string` |
| `audio_device_has_input` | `(dev: AudioDevice) -> bool` |
| `audio_device_has_output` | `(dev: AudioDevice) -> bool` |

### `audio/lattice_allpass.flow`

Many-pole lattice all-pass — Schur reflections, fast per-sample modulation Import: import "stdlib/audio/lattice_allpass.flow"

**Structs:** `LatticeAllpass`, `LatticeAllpassDesign`

**Functions:**

| Name | Signature |
|------|-----------|
| `lattice_allpass_design_from_poles` | `(
    poles: ptr<f64>,
    pole_count: i32,
    a_buf: ptr<f64>,
    ctrl_buf: ptr<f64>,
    apow_buf: ptr<f64>,
    blk_buf: ptr<f64>,
    na_buf: ptr<f64>
) -> LatticeAllpassDesign` |
| `lattice_allpass_new` | `(
    design: LatticeAllpassDesign,
    mod_depth: f32,
    mod_rate_hz: f32
) -> LatticeAllpass` |
| `lattice_allpass_modulate` | `(ap: LatticeAllpass, rate: SampleRate) -> LatticeAllpass` |
| `lattice_allpass_tick` | `(ap: LatticeAllpass, input: f32) -> LatticeAllpass` |
| `lattice_allpass_output` | `(ap: LatticeAllpass) -> f32` |
| `lattice_allpass_reset` | `(ap: LatticeAllpass) -> LatticeAllpass` |
| `lattice_allpass_block_energy` | `(samples: ptr<f32>, count: i32) -> f32` |

### `audio/livecode.flow`

Livecode Module - Ultra-Easy Audio Programming  THE EASIEST WAY TO MAKE SOUND IN ANY PROGRAMMING LANGUAGE.

**Structs:** `LiveContext`

**Functions:**

| Name | Signature |
|------|-----------|
| `live_context_new` | `() -> LiveContext` |
| `live_context_44k_120bpm` | `() -> LiveContext` |
| `bass` | `(note: i32) -> f32` |
| `lead` | `(note: i32) -> f32` |
| `pad` | `(note: i32) -> f32` |
| `pluck` | `(note: i32) -> f32` |
| `organ` | `(note: i32) -> f32` |
| `kick` | `() -> f32` |
| `snare` | `() -> f32` |
| `hat` | `() -> f32` |
| `hat_open` | `() -> f32` |
| `clap` | `() -> f32` |
| `kick_on_beat` | `(clock: Clock, pos: i64) -> bool` |
| `snare_on_backbeat` | `(clock: Clock, pos: i64) -> bool` |
| `hat_on_eighth` | `(clock: Clock, pos: i64) -> bool` |
| `hat_on_sixteenth` | `(clock: Clock, pos: i64) -> bool` |
| `pattern_4` | `(notes: array<i32, 4>, clock: Clock, pos: i64) -> f32` |
| `pattern_8` | `(notes: array<i32, 8>, clock: Clock, pos: i64) -> f32` |
| `chord_progression` | `(chords: array<array<i32, 3>, 4>, clock: Clock, pos: i64) -> f32` |
| `euclidean_hit` | `(k: i32, n: i32, step_val: i32) -> bool` |
| `euclidean_pattern` | `(k: i32, n: i32, clock: Clock, pos: i64) -> f32` |
| `scale_note` | `(root: i32, scale_type: i32, degree: i32) -> i32` |
| `with_delay` | `(input: f32, clock: Clock) -> f32` |
| `with_distortion` | `(input: f32, amount: f32) -> f32` |
| `with_reverb` | `(input: f32, size: f32) -> f32` |
| `with_bitcrush` | `(input: f32, bits: i32) -> f32` |
| `house_beat` | `(clock: Clock, pos: i64) -> f32` |
| `bass_pattern_simple` | `(root: i32, clock: Clock, pos: i64) -> f32` |
| `arpeggio` | `(chord: array<i32, 3>, clock: Clock, pos: i64) -> f32` |
| `master_out` | `(input: f32) -> f32` |
| `master_out_stereo` | `(left: f32, right: f32) -> Frame` |

### `audio/notation.flow`

Musical Notation Module - Load Music from Files  Simple text-based notation for livecoding:

**Structs:** `MusicNote`, `NotationReader`

**Functions:**

| Name | Signature |
|------|-----------|
| `parse_note_name` | `(name: string) -> i32` |
| `parse_note_simple` | `(note_str: string, duration: i32) -> MusicNote` |
| `notation_reader_new` | `() -> NotationReader` |
| `notation_load_file` | `(reader: ptr<NotationReader>, path: string) -> bool` |
| `load_file` | `(reader: ptr<NotationReader>, path: string) -> bool` |
| `get_note_count` | `(reader: ptr<NotationReader>) -> i32` |
| `get_note` | `(reader: ptr<NotationReader>, idx: i32) -> MusicNote` |
| `parse_line` | `(reader: ptr<NotationReader>, line: string) -> bool` |
| `load_notation` | `(path: string) -> NotationReader` |
| `note_name_to_midi` | `(note: i32, octave: i32) -> i32` |
| `note_from_name` | `(name: i32, octave: i32, duration: i32) -> MusicNote` |

### `audio/oscillators.flow`

Audio Oscillators Module  Phase-based oscillators and waveshaping functions.

**Structs:** `Phasor`, `NoiseState`, `LFO`

**Constants:**

- `TWO_PI: f64`
- `PI: f64`

**Functions:**

| Name | Signature |
|------|-----------|
| `phasor_new` | `(freq: f64, rate: SampleRate) -> Phasor` |
| `phasor_new_with_phase` | `(freq: f64, rate: SampleRate, initial_phase: f64) -> Phasor` |
| `phasor_tick` | `(p: Phasor) -> Phasor` |
| `phasor_value` | `(p: Phasor) -> f64` |
| `phasor_set_freq` | `(p: Phasor, freq: f64, rate: SampleRate) -> Phasor` |
| `phasor_reset` | `(p: Phasor) -> Phasor` |
| `phasor_sync` | `(p: Phasor, target_phase: f64) -> Phasor` |
| `sine` | `(phase: f64) -> f32` |
| `saw` | `(phase: f64) -> f32` |
| `saw_reverse` | `(phase: f64) -> f32` |
| `square` | `(phase: f64) -> f32` |
| `pulse` | `(phase: f64, width: f64) -> f32` |
| `triangle` | `(phase: f64) -> f32` |
| `saw_blep` | `(phase: f64, increment: f64) -> f32` |
| `square_blep` | `(phase: f64, increment: f64) -> f32` |
| `noise_new` | `(seed: i64) -> NoiseState` |
| `noise_tick` | `(n: NoiseState) -> NoiseState` |
| `noise_value` | `(n: NoiseState) -> f32` |
| `white_noise` | `(n: NoiseState) -> f32` |
| `lfo_new` | `(rate_hz: f64, sample_rate: SampleRate, depth: f32) -> LFO` |
| `lfo_tick` | `(l: LFO) -> LFO` |
| `lfo_sine` | `(l: LFO) -> f32` |
| `lfo_triangle` | `(l: LFO) -> f32` |
| `lfo_unipolar` | `(l: LFO) -> f32` |

### `audio/processor.flow`

Audio Processor Module  Trait-based interface for audio processing components.

**Structs:** `GainProcessor`, `HardClipper`, `SoftClipper`, `DCOffset`, `StereoWidth`, `StereoPan`

**Functions:**

| Name | Signature |
|------|-----------|
| `gain_processor_new` | `(gain_db: f32) -> GainProcessor` |
| `gain_processor_set_db` | `(g: GainProcessor, db: f32) -> GainProcessor` |
| `gain_processor_set_linear` | `(g: GainProcessor, linear: f32) -> GainProcessor` |
| `hard_clipper_new` | `(threshold: f32) -> HardClipper` |
| `soft_clipper_new` | `(drive: f32) -> SoftClipper` |
| `dc_offset_new` | `(offset: f32) -> DCOffset` |
| `stereo_width_new` | `(width: f32) -> StereoWidth` |
| `stereo_pan_new` | `(pan: f32) -> StereoPan` |
| `process_with_gain_clip` | `(sample: f32, gain: f32, threshold: f32) -> f32` |
| `crossfade` | `(a: f32, b: f32, mix: f32) -> f32` |
| `crossfade_equal_power` | `(a: f32, b: f32, mix: f32) -> f32` |

### `audio/scales.flow`

Music Theory Module - Scales, Chords, and Note Helpers  Makes music theory incredibly easy - easier than any other language.

**Functions:**

| Name | Signature |
|------|-----------|
| `note_to_midi` | `(note_name: string) -> i32` |
| `note_C` | `(octave: i32) -> i32` |
| `note_Cs` | `(octave: i32) -> i32` |
| `note_Db` | `(octave: i32) -> i32` |
| `note_D` | `(octave: i32) -> i32` |
| `note_Ds` | `(octave: i32) -> i32` |
| `note_Eb` | `(octave: i32) -> i32` |
| `note_E` | `(octave: i32) -> i32` |
| `note_F` | `(octave: i32) -> i32` |
| `note_Fs` | `(octave: i32) -> i32` |
| `note_Gb` | `(octave: i32) -> i32` |
| `note_G` | `(octave: i32) -> i32` |
| `note_Gs` | `(octave: i32) -> i32` |
| `note_Ab` | `(octave: i32) -> i32` |
| `note_A` | `(octave: i32) -> i32` |
| `note_As` | `(octave: i32) -> i32` |
| `note_Bb` | `(octave: i32) -> i32` |
| `note_B` | `(octave: i32) -> i32` |
| `C4` | `() -> i32` |
| `A4` | `() -> i32` |
| `C3` | `() -> i32` |
| `C5` | `() -> i32` |
| `scale_major` | `(root: i32) -> array<i32, 7>` |
| `scale_minor` | `(root: i32) -> array<i32, 7>` |
| `scale_pentatonic_major` | `(root: i32) -> array<i32, 5>` |
| `scale_pentatonic_minor` | `(root: i32) -> array<i32, 5>` |
| `scale_blues` | `(root: i32) -> array<i32, 6>` |
| `scale_chromatic` | `(root: i32) -> array<i32, 12>` |
| `scale_whole_tone` | `(root: i32) -> array<i32, 6>` |
| `scale_dorian` | `(root: i32) -> array<i32, 7>` |
| `scale_phrygian` | `(root: i32) -> array<i32, 7>` |
| `scale_lydian` | `(root: i32) -> array<i32, 7>` |
| `scale_mixolydian` | `(root: i32) -> array<i32, 7>` |
| `chord_major` | `(root: i32) -> array<i32, 3>` |
| `chord_minor` | `(root: i32) -> array<i32, 3>` |
| `chord_dim` | `(root: i32) -> array<i32, 3>` |
| `chord_aug` | `(root: i32) -> array<i32, 3>` |
| `chord_maj7` | `(root: i32) -> array<i32, 4>` |
| `chord_min7` | `(root: i32) -> array<i32, 4>` |
| `chord_dom7` | `(root: i32) -> array<i32, 4>` |
| `chord_sus2` | `(root: i32) -> array<i32, 3>` |
| `chord_sus4` | `(root: i32) -> array<i32, 3>` |
| `chord_power` | `(root: i32) -> array<i32, 2>` |
| `midi_to_freq_accurate` | `(note: i32) -> f32` |
| `freq` | `(midi_note: i32) -> f32` |
| `progression_145` | `(root: i32) -> array<array<i32, 3>, 4>` |
| `progression_pop` | `(root: i32) -> array<array<i32, 3>, 4>` |
| `progression_blues` | `(root: i32) -> array<array<i32, 3>, 4>` |
| `transpose` | `(note: i32, semitones: i32) -> i32` |
| `octave_up` | `(note: i32) -> i32` |
| `octave_down` | `(note: i32) -> i32` |
| `chord_invert` | `(chord: array<i32, 3>) -> array<i32, 3>` |
| `is_in_scale` | `(note: i32, scale: array<i32, 7>) -> bool` |

### `audio/simd.flow`

Audio SIMD Helpers  Backed by runtime/audio_simd.c. These are safe CPU fast paths that can be

**Functions:**

| Name | Signature |
|------|-----------|
| `audio_gain_interleaved_f32` | `(data: ptr<f32>, frames: i32, channels: i32, gain: f32) -> void` |
| `audio_gain_interleaved_f32_fast` | `(data: ptr<f32>, frames: i32, channels: i32, gain: f32) -> void` |
| `audio_mix_interleaved_f32` | `(dst: ptr<f32>, src: ptr<f32>, frames: i32, channels: i32) -> void` |
| `audio_copy_interleaved_f32` | `(dst: ptr<f32>, src: ptr<f32>, frames: i32, channels: i32) -> void` |
| `audio_mix_interleaved_f32_fast` | `(dst: ptr<f32>, src: ptr<f32>, frames: i32, channels: i32) -> void` |
| `audio_copy_interleaved_f32_fast` | `(dst: ptr<f32>, src: ptr<f32>, frames: i32, channels: i32) -> void` |

### `audio/synth.flow`

Synth Presets Module - Ready-to-Use Instruments  Pre-configured synthesizers that sound good out of the box.

**Structs:** `Synth`, `ADSREnvelope`

**Functions:**

| Name | Signature |
|------|-----------|
| `synth_bass` | `() -> Synth` |
| `synth_lead` | `() -> Synth` |
| `synth_pad` | `() -> Synth` |
| `synth_pluck` | `() -> Synth` |
| `synth_organ` | `() -> Synth` |
| `synth_fm` | `() -> Synth` |
| `synth_sub` | `() -> Synth` |
| `synth_brass` | `() -> Synth` |
| `synth_tick` | `(synth: Synth, freq: f32, gate: bool) -> f32` |

### `audio.flow`

Audio Module - Core Types and Operations  Real-time audio processing primitives with proper DSP nomenclature.

**Structs:** `SampleRate`, `Samples`, `Seconds`, `Frame`, `Layout`, `Buffer`, `AudioBufferF32`

**Functions:**

| Name | Signature |
|------|-----------|
| `sample_rate_new` | `(hz: f64) -> SampleRate` |
| `samples_new` | `(count: i64) -> Samples` |
| `seconds_new` | `(value: f64) -> Seconds` |
| `sample_rate_44100` | `() -> SampleRate` |
| `sample_rate_48000` | `() -> SampleRate` |
| `sample_rate_96000` | `() -> SampleRate` |
| `samples_to_seconds` | `(s: Samples, rate: SampleRate) -> Seconds` |
| `seconds_to_samples` | `(t: Seconds, rate: SampleRate) -> Samples` |
| `samples_per_ms` | `(rate: SampleRate) -> f64` |
| `ms_to_samples` | `(ms: f64, rate: SampleRate) -> Samples` |
| `frame_new` | `(left: f32, right: f32) -> Frame` |
| `frame_mono` | `(value: f32) -> Frame` |
| `frame_zero` | `() -> Frame` |
| `frame_mix` | `(a: Frame, b: Frame) -> Frame` |
| `frame_scale` | `(f: Frame, gain: f32) -> Frame` |
| `frame_pan` | `(value: f32, pan: f32) -> Frame` |
| `frame_to_mono` | `(f: Frame) -> f32` |
| `layout_interleaved` | `() -> Layout` |
| `layout_planar` | `() -> Layout` |
| `buffer_create` | `(frames: i32, channels: i32) -> Buffer` |
| `audio_buffer_empty_f32` | `() -> AudioBufferF32` |
| `audio_buffer_alloc_f32` | `(frames: i32, channels: i32, layout: Layout) -> AudioBufferF32` |
| `audio_buffer_free_f32` | `(buf: AudioBufferF32) -> void` |
| `audio_buffer_index` | `(buf: AudioBufferF32, frame: i32, channel: i32) -> i32` |
| `audio_buffer_get_f32` | `(buf: AudioBufferF32, frame: i32, channel: i32) -> f32` |
| `audio_buffer_set_f32` | `(buf: AudioBufferF32, frame: i32, channel: i32, value: f32) -> void` |
| `audio_buffer_zero_f32` | `(buf: AudioBufferF32) -> void` |
| `audio_buffer_copy_interleaved_f32` | `(dst: AudioBufferF32, src: AudioBufferF32, frames: i32) -> void` |
| `audio_buffer_add_interleaved_f32` | `(dst: AudioBufferF32, src: AudioBufferF32, frames: i32) -> void` |
| `audio_buffer_frame_count` | `(buf: AudioBufferF32) -> i32` |
| `audio_buffer_channel_count` | `(buf: AudioBufferF32) -> i32` |
| `buffer_stereo` | `(frames: i32) -> Buffer` |
| `buffer_mono` | `(frames: i32) -> Buffer` |
| `buffer_sample_count` | `(buf: Buffer) -> i32` |
| `buffer_duration` | `(buf: Buffer, rate: SampleRate) -> Seconds` |
| `linear_to_db` | `(linear: f32) -> f32` |
| `db_to_linear` | `(db: f32) -> f32` |
| `midi_to_freq` | `(note: i32) -> f32` |
| `freq_to_period_samples` | `(freq: f32, rate: SampleRate) -> f32` |
| `clip` | `(sample: f32) -> f32` |
| `soft_clip` | `(sample: f32) -> f32` |
| `frame_clip` | `(f: Frame) -> Frame` |

### `autodiff.flow`

FLOW Automatic Differentiation Library  Two modes:

**Functions:**

| Name | Signature |
|------|-----------|
| `dual_var` | `(x: f32) -> Dual` |
| `dual_const` | `(x: f32) -> Dual` |
| `dual_add` | `(a: Dual, b: Dual) -> Dual` |
| `dual_sub` | `(a: Dual, b: Dual) -> Dual` |
| `dual_mul` | `(a: Dual, b: Dual) -> Dual` |
| `dual_div` | `(a: Dual, b: Dual) -> Dual` |
| `dual_pow` | `(x: Dual, n: f32) -> Dual` |
| `dual_sq` | `(x: Dual) -> Dual` |
| `dual_sqrt` | `(x: Dual) -> Dual` |
| `dual_exp` | `(x: Dual) -> Dual` |
| `dual_log` | `(x: Dual) -> Dual` |
| `dual_sin` | `(x: Dual) -> Dual` |
| `dual_cos` | `(x: Dual) -> Dual` |
| `dual_tan` | `(x: Dual) -> Dual` |
| `dual_relu` | `(x: Dual) -> Dual` |
| `dual_sigmoid` | `(x: Dual) -> Dual` |
| `dual_tanh` | `(x: Dual) -> Dual` |
| `numerical_grad` | `(f_plus: f32, f_minus: f32, epsilon: f32) -> f32` |
| `dual_val` | `(d: Dual) -> f32` |
| `dual_grad` | `(d: Dual) -> f32` |
| `dx` | `(x: f32) -> Dual` |
| `d` | `(x: f32) -> Dual` |
| `add` | `(a: Dual, b: Dual) -> Dual` |
| `add` | `(a: Dual, b: f32) -> Dual` |
| `add` | `(a: f32, b: Dual) -> Dual` |
| `sub` | `(a: Dual, b: Dual) -> Dual` |
| `sub` | `(a: Dual, b: f32) -> Dual` |
| `sub` | `(a: f32, b: Dual) -> Dual` |
| `mul` | `(a: Dual, b: Dual) -> Dual` |
| `mul` | `(a: Dual, b: f32) -> Dual` |
| `mul` | `(a: f32, b: Dual) -> Dual` |
| `div` | `(a: Dual, b: Dual) -> Dual` |
| `ddiv` | `(a: Dual, b: Dual) -> Dual` |
| `div` | `(a: Dual, b: f32) -> Dual` |
| `divs` | `(a: Dual, b: f32) -> Dual` |
| `div` | `(a: f32, b: Dual) -> Dual` |
| `rdiv` | `(a: f32, b: Dual) -> Dual` |
| `addc` | `(a: f32, b: Dual) -> Dual` |
| `rsub` | `(a: f32, b: Dual) -> Dual` |
| `smul` | `(a: f32, b: Dual) -> Dual` |
| `scale` | `(a: f32, b: Dual) -> Dual` |
| `add` | `(a: f32, b: f32) -> f32` |
| `sub` | `(a: f32, b: f32) -> f32` |
| `mul` | `(a: f32, b: f32) -> f32` |
| `neg` | `(a: Dual) -> Dual` |
| `sigmoid` | `(x: Dual) -> Dual` |
| `ln` | `(x: Dual) -> Dual` |
| `log` | `(x: Dual) -> Dual` |
| `e` | `(x: Dual) -> Dual` |
| `sinD` | `(x: Dual) -> Dual` |
| `cosD` | `(x: Dual) -> Dual` |
| `tanhD` | `(x: Dual) -> Dual` |
| `sq` | `(x: Dual) -> Dual` |
| `cube` | `(x: Dual) -> Dual` |
| `pow4` | `(x: Dual) -> Dual` |
| `sq_diff` | `(x: Dual, c: f32) -> Dual` |
| `linear` | `(x: Dual, a: f32, b: f32) -> Dual` |
| `quadratic` | `(x: Dual, a: f32, b: f32, c: f32) -> Dual` |
| `sin_scaled` | `(x: Dual, a: f32) -> Dual` |
| `cos_scaled` | `(x: Dual, a: f32) -> Dual` |
| `exp_scaled` | `(x: Dual, a: f32) -> Dual` |
| `chain_add` | `(f: Dual, g: Dual) -> Dual` |
| `chain_mul` | `(f: Dual, g: Dual) -> Dual` |
| `weighted_sum` | `(f: Dual, a: f32, g: Dual, b: f32) -> Dual` |
| `sum3` | `(a: Dual, b: Dual, c: Dual) -> Dual` |

### `autodiff_reverse.flow`

Reverse-Mode Automatic Differentiation Helpers  Provides operations that return both value AND local gradient,

**Functions:**

| Name | Signature |
|------|-----------|
| `op_add` | `(a: f32, b: f32) -> BinaryResult` |
| `op_sub` | `(a: f32, b: f32) -> BinaryResult` |
| `op_mul` | `(a: f32, b: f32) -> BinaryResult` |
| `op_div` | `(a: f32, b: f32) -> BinaryResult` |
| `op_sq` | `(x: f32) -> UnaryResult` |
| `op_sqrt` | `(x: f32) -> UnaryResult` |
| `op_exp` | `(x: f32) -> UnaryResult` |
| `op_log` | `(x: f32) -> UnaryResult` |
| `op_sigmoid` | `(x: f32) -> UnaryResult` |
| `op_sin` | `(x: f32) -> UnaryResult` |
| `op_cos` | `(x: f32) -> UnaryResult` |
| `op_tanh` | `(x: f32) -> UnaryResult` |
| `op_relu` | `(x: f32) -> UnaryResult` |
| `op_neg` | `(x: f32) -> UnaryResult` |

### `blas.flow`

BLAS/LAPACK bindings via Apple Accelerate (or OpenBLAS on Linux) Import: import "stdlib/blas.flow"

**Functions:**

| Name | Signature |
|------|-----------|
| `mat_new` | `(rows: i32, cols: i32) -> Mat` |
| `mat_free` | `(m: Mat) -> void` |
| `mat_wrap` | `(data: ptr<f64>, rows: i32, cols: i32) -> Mat` |
| `mat_clone` | `(m: Mat) -> Mat` |
| `mat_get` | `(m: Mat, i: i32, j: i32) -> f64` |
| `mat_set` | `(m: Mat, i: i32, j: i32, val: f64) -> void` |
| `gemm` | `(A: Mat, B: Mat, C: Mat) -> void` |
| `gemm_alpha_beta` | `(alpha: f64, A: Mat, B: Mat, beta: f64, C: Mat) -> void` |
| `gemv` | `(A: Mat, x: ptr<f64>, y: ptr<f64>) -> void` |
| `dot` | `(x: ptr<f64>, y: ptr<f64>, n: i32) -> f64` |
| `norm2` | `(x: ptr<f64>, n: i32) -> f64` |
| `axpy` | `(alpha: f64, x: ptr<f64>, y: ptr<f64>, n: i32) -> void` |
| `scal` | `(alpha: f64, x: ptr<f64>, n: i32) -> void` |
| `solve` | `(A: Mat, b: ptr<f64>, x: ptr<f64>) -> i32` |
| `getrf` | `(A: Mat, pivots: ptr<i32>) -> i32` |
| `lu_factor` | `(A: Mat, pivots: ptr<i32>) -> i32` |
| `matmul` | `(A: Mat, B: Mat) -> Mat` |
| `transpose` | `(A: Mat) -> Mat` |
| `eye` | `(n: i32) -> Mat` |
| `zeros` | `(rows: i32, cols: i32) -> Mat` |
| `ones` | `(rows: i32, cols: i32) -> Mat` |

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

| Name | Signature |
|------|-----------|
| `dlqr_diag_q_scalar_u` | `(
    ad: ptr<f64>,
    bd: ptr<f64>,
    q_diag: ptr<f64>,
    r: f64,
    n: i32,
    k_out: ptr<f64>,
    max_iter: i32
) -> i32` |
| `lqr_diag_q` | `(ad: ptr<f64>, bd: ptr<f64>, q_diag: ptr<f64>, r: f64,
                           n: i32, k_out: ptr<f64>, max_iter: i32) -> i32` |

### `dynamics/pde.flow`

PDE helpers (pattern-adoption #163). Stdlib MVP for field evolution without `field` / `boundary` grammar yet. Import: import "stdlib/dynamics/pde.flow"

**Functions:**

| Name | Signature |
|------|-----------|
| `laplacian_1d_at` | `(u: ptr<f64>, i: i32, dx: f64) -> f64` |
| `laplacian_1d` | `(u: ptr<f64>, out: ptr<f64>, n: i32, dx: f64) -> void` |
| `heat_euler_step_1d` | `(
    u: ptr<f64>,
    next: ptr<f64>,
    n: i32,
    r: f64,
    left_bc: f64,
    right_bc: f64
) -> void` |
| `field_copy_1d` | `(src: ptr<f64>, dst: ptr<f64>, n: i32) -> void` |

### `dynamics/portrait.flow`

Phase-portrait trail helpers (pattern-adoption #165). Ring-buffer + project helpers until `represent phase_portrait` lowers. Import: import "stdlib/dynamics/portrait.flow"

**Functions:**

| Name | Signature |
|------|-----------|
| `trail_push_2d` | `(
    xs: ptr<f64>,
    zs: ptr<f64>,
    capacity: i32,
    head: ptr<i32>,
    count: ptr<i32>,
    x: f64,
    z: f64
) -> void` |
| `trail_index` | `(head: i32, count: i32, capacity: i32, i: i32) -> i32` |
| `project_axis` | `(v: f64, vmin: f64, vmax: f64, width: i32, pad: i32) -> i32` |

### `dynamics/schur_lattice.flow`

Schur / lattice / orthogonal-colligation route for all-pass synthesis Import: import "stdlib/dynamics/schur_lattice.flow"

*No `export` items found (internal / extern-only module).*

### `dynamics/state_space.flow`

State-space simulation, controllability, transformations Import: import "stdlib/dynamics/state_space.flow"

**Functions:**

| Name | Signature |
|------|-----------|
| `state_step` | `(sys: DynamicalSystem, x: ptr<f64>, u: ptr<f64>, x_next: ptr<f64>) -> void` |
| `plant_step` | `(sys: DynamicalSystem, x: ptr<f64>, u: ptr<f64>, x_next: ptr<f64>) -> void` |

### `dynamics/wfc.flow`

Wave Function Collapse (constraint propagation on tile grids) Import: import "stdlib/dynamics/wfc.flow"

*No `export` items found (internal / extern-only module).*

### `dynamics/wfc_ga_coupling.flow`

GA + WFC coupled guidance for state-space evolution Import: import "stdlib/dynamics/wfc_ga_coupling.flow"

*No `export` items found (internal / extern-only module).*

### `dynamics.flow`

Flow Dynamical Systems Standard Library  Declarative DSL via structs (no new keywords required):

*No `export` items found (internal / extern-only module).*

### `gfx.flow`

gfx: explicit native graphics API (macOS / Linux SDL2 / Windows)  Backend: runtime/gfx_macos.m, runtime/gfx_linux.c, runtime/gfx_windows.c

**Functions:**

| Name | Signature |
|------|-----------|
| `gfx_open` | `(w: i32, h: i32, title: string) -> Gfx` |
| `gfx_close` | `(g: Gfx) -> void` |
| `gfx_poll` | `(g: Gfx) -> void` |
| `gfx_should_close` | `(g: Gfx) -> bool` |
| `gfx_key_down` | `(g: Gfx, keycode: i32) -> bool` |
| `gfx_clear` | `(g: Gfx, r: i32, g2: i32, b: i32) -> void` |
| `gfx_fill_rect` | `(g: Gfx, x: i32, y: i32, w: i32, h: i32, r: i32, g2: i32, b: i32) -> void` |
| `gfx_present` | `(g: Gfx) -> void` |
| `gfx_frame_pump` | `(g: Gfx) -> bool` |
| `gfx_run` | `(g: Gfx, max_frames: i32) -> i32` |

### `gpu_gradients.flow`

GPU gradient helpers (MVP)  Thin wrappers over Metal elementwise mul / mul-backward kernels.

**Functions:**

| Name | Signature |
|------|-----------|
| `gpu_mul_f32` | `(out: GpuBuffer, a: GpuBuffer, b: GpuBuffer, n: i64) -> i32` |
| `gpu_mul_backward_a_f32` | `(grad_a: GpuBuffer, grad_out: GpuBuffer, b: GpuBuffer, n: i64) -> i32` |
| `gpu_mul_backward_b_f32` | `(grad_b: GpuBuffer, grad_out: GpuBuffer, a: GpuBuffer, n: i64) -> i32` |

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

| Name | Signature |
|------|-----------|
| `gpu_available` | `() -> bool` |
| `gpu_backend_name` | `() -> string` |
| `gpu_null_buffer` | `() -> GpuBuffer` |
| `gpu_is_null` | `(buf: GpuBuffer) -> bool` |
| `gpu_alloc_flags` | `(size: i64, flags: i32) -> GpuBuffer` |
| `gpu_alloc` | `(size: i64) -> GpuBuffer` |
| `gpu_alloc_unified` | `(size: i64) -> GpuBuffer` |
| `gpu_alloc_private` | `(size: i64) -> GpuBuffer` |
| `gpu_alloc_f32` | `(count: i64) -> GpuBuffer` |
| `gpu_alloc_f64` | `(count: i64) -> GpuBuffer` |
| `gpu_alloc_i32` | `(count: i64) -> GpuBuffer` |
| `gpu_free` | `(buf: GpuBuffer) -> void` |
| `gpu_size` | `(buf: GpuBuffer) -> i64` |
| `gpu_host_ptr` | `(buf: GpuBuffer) -> ptr<void>` |
| `gpu_is_unified` | `(buf: GpuBuffer) -> bool` |
| `gpu_copy_h2d` | `(dst: GpuBuffer, src: ptr<void>, nbytes: i64) -> i32` |
| `gpu_copy_d2h` | `(dst: ptr<void>, src: GpuBuffer, nbytes: i64) -> i32` |
| `gpu_copy_h2d_i32` | `(dst: GpuBuffer, src: ptr<i32>, nbytes: i64) -> i32` |
| `gpu_copy_d2h_i32` | `(dst: ptr<i32>, src: GpuBuffer, nbytes: i64) -> i32` |
| `gpu_copy_h2d_f32` | `(dst: GpuBuffer, src: ptr<f32>, nbytes: i64) -> i32` |
| `gpu_copy_d2h_f32` | `(dst: ptr<f32>, src: GpuBuffer, nbytes: i64) -> i32` |
| `gpu_copy_d2d` | `(dst: GpuBuffer, src: GpuBuffer, nbytes: i64) -> i32` |
| `gpu_sync` | `() -> void` |
| `gpu_allocate` | `(size: i64) -> GpuBuffer` |
| `gpu_copy_to_device` | `(dst: GpuBuffer, src: ptr<void>, nbytes: i64) -> i32` |
| `gpu_copy_from_device` | `(dst: ptr<void>, src: GpuBuffer, nbytes: i64) -> i32` |
| `gpu_copy_device_to_device` | `(dst: GpuBuffer, src: GpuBuffer, nbytes: i64) -> i32` |
| `unified_allocate` | `(size: i64) -> GpuBuffer` |

### `gpu_sim.flow`

GPU simulation layer (CPU-backed) to model DeviceContext/Queue/Buffer/Layouts. This is a compatibility + teaching layer to mirror Mojo-style APIs.

*No `export` items found (internal / extern-only module).*

### `io.flow`

**Functions:**

| Name | Signature |
|------|-----------|
| `print_benchmark` | `(name: string, time: f64) -> void` |

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

| Name | Signature |
|------|-----------|
| `add` | `(a: f32, b: f32) -> f32` |
| `subtract` | `(a: f32, b: f32) -> f32` |
| `multiply` | `(a: f32, b: f32) -> f32` |
| `divide` | `(a: f32, b: f32) -> f32` |
| `power` | `(base: f32, exponent: f32) -> f32` |
| `sin` | `(x: f32) -> f32` |
| `cos` | `(x: f32) -> f32` |
| `sqrt` | `(x: f32) -> f32` |
| `fabs` | `(x: f32) -> f32` |
| `abs` | `(x: f32) -> f32` |
| `tan` | `(x: f32) -> f32` |
| `log` | `(x: f32) -> f32` |
| `exp` | `(x: f32) -> f32` |
| `fibonacci` | `(n: i32) -> i32` |
| `gcd` | `(a: i32, b: i32) -> i32` |
| `lcm` | `(a: i32, b: i32) -> i32` |
| `is_prime` | `(n: i32) -> bool` |
| `factorial_big` | `(n: i32) -> i64` |

### `memory.flow`

Manual memory management — real libc heap (C backend)  Flow has no GC. Heap memory is yours to allocate and free.

**Structs:** `Arena`

**Functions:**

| Name | Signature |
|------|-----------|
| `sizeof_i8` | `() -> i64` |
| `sizeof_i32` | `() -> i64` |
| `sizeof_i64` | `() -> i64` |
| `sizeof_f32` | `() -> i64` |
| `sizeof_f64` | `() -> i64` |
| `sizeof_ptr` | `() -> i64` |
| `alignof_i32` | `() -> i64` |
| `alignof_i64` | `() -> i64` |
| `alignof_f32` | `() -> i64` |
| `alignof_f64` | `() -> i64` |
| `is_power_of_two` | `(value: i64) -> bool` |
| `align_up` | `(size: i64, alignment: i64) -> i64` |
| `align_down` | `(size: i64, alignment: i64) -> i64` |
| `alloc_bytes` | `(size: i64) -> ptr<void>` |
| `alloc_zeroed` | `(size: i64) -> ptr<void>` |
| `alloc_i32` | `(count: i64) -> ptr<i32>` |
| `alloc_f32` | `(count: i64) -> ptr<f32>` |
| `alloc_f64` | `(count: i64) -> ptr<f64>` |
| `memory_zero_i32` | `(p: ptr<i32>, count: i64) -> void` |
| `memory_copy_i32` | `(dst: ptr<i32>, src: ptr<i32>, count: i64) -> void` |
| `arena_create` | `(capacity: i64) -> Arena` |
| `arena_alloc` | `(arena: ptr<Arena>, size: i64) -> ptr<void>` |
| `arena_alloc_i32` | `(arena: ptr<Arena>, count: i64) -> ptr<i32>` |
| `arena_alloc_f32` | `(arena: ptr<Arena>, count: i64) -> ptr<f32>` |
| `arena_reset` | `(arena: ptr<Arena>) -> void` |
| `arena_destroy` | `(arena: ptr<Arena>) -> void` |
| `arena_used` | `(arena: Arena) -> i64` |
| `arena_remaining` | `(arena: Arena) -> i64` |

### `memory_simple.flow`

Memory Management Module Provides low-level memory allocation, manipulation, and safety functions

**Structs:** `MemoryPool`

**Functions:**

| Name | Signature |
|------|-----------|
| `malloc` | `(size: i32) -> i32` |
| `calloc` | `(nmemb: i32, size: i32) -> i32` |
| `realloc` | `(ptr: i32, size: i32) -> i32` |
| `free` | `(ptr: i32) -> void` |
| `aligned_alloc` | `(alignment: i32, size: i32) -> i32` |
| `memcpy` | `(dest: i32, src: i32, n: i32) -> i32` |
| `memmove` | `(dest: i32, src: i32, n: i32) -> i32` |
| `memset` | `(dest: i32, c: i32, n: i32) -> i32` |
| `memcmp` | `(s1: i32, s2: i32, n: i32) -> i32` |
| `is_power_of_two` | `(value: i32) -> bool` |
| `alignof_i32` | `() -> i32` |
| `alignof_f32` | `() -> i32` |
| `alignof_i8` | `() -> i32` |
| `sizeof_i32` | `() -> i32` |
| `sizeof_f32` | `() -> i32` |
| `sizeof_i8` | `() -> i32` |
| `offset_of_Point` | `(field: string) -> i32` |
| `is_aligned` | `(ptr: i32, alignment: i32) -> bool` |
| `align_up` | `(size: i32, alignment: i32) -> i32` |
| `align_down` | `(size: i32, alignment: i32) -> i32` |
| `memory_check` | `(ptr: i32, size: i32) -> bool` |
| `memory_check_write` | `(ptr: i32, size: i32) -> bool` |
| `memory_fill_pattern` | `(ptr: i32, pattern: i32, count: i32) -> void` |
| `memory_zero` | `(ptr: i32, size: i32) -> void` |
| `memory_copy_nonoverlapping` | `(dest: i32, src: i32, n: i32) -> void` |
| `memory_copy_overlapping` | `(dest: i32, src: i32, n: i32) -> void` |
| `alloca` | `(size: i32) -> i32` |
| `stack_array_i32` | `(count: i32) -> i32` |
| `stack_array_f32` | `(count: i32) -> i32` |
| `memory_pool_create` | `(size: i32) -> MemoryPool` |
| `memory_pool_alloc` | `(pool: MemoryPool, size: i32, alignment: i32) -> i32` |
| `memory_pool_reset` | `(pool: MemoryPool) -> void` |
| `memory_pool_destroy` | `(pool: MemoryPool) -> void` |
| `memory_dump` | `(ptr: i32, size: i32, bytes_per_line: i32) -> void` |
| `memory_validate` | `(ptr: i32, size: i32) -> bool` |
| `format_hex` | `(value: i32) -> string` |
| `format_hex_ptr` | `(ptr: i32) -> string` |

### `memory_working.flow`

Simple Memory Management Module Basic memory allocation and manipulation functions

**Structs:** `MemoryPool`

**Functions:**

| Name | Signature |
|------|-----------|
| `malloc` | `(size: i32) -> i32` |
| `calloc` | `(nmemb: i32, size: i32) -> i32` |
| `realloc` | `(ptr: i32, size: i32) -> i32` |
| `free` | `(ptr: i32) -> i32` |
| `aligned_alloc` | `(alignment: i32, size: i32) -> i32` |
| `memcpy` | `(dest: i32, src: i32, n: i32) -> i32` |
| `memmove` | `(dest: i32, src: i32, n: i32) -> i32` |
| `memset` | `(dest: i32, c: i32, n: i32) -> i32` |
| `memcmp` | `(s1: i32, s2: i32, n: i32) -> i32` |
| `is_power_of_two` | `(value: i32) -> bool` |
| `alignof_i32` | `() -> i32` |
| `alignof_f32` | `() -> i32` |
| `alignof_i8` | `() -> i32` |
| `sizeof_i32` | `() -> i32` |
| `sizeof_f32` | `() -> i32` |
| `sizeof_i8` | `() -> i32` |
| `offset_of_Point` | `(field: string) -> i32` |
| `is_aligned` | `(ptr: i32, alignment: i32) -> bool` |
| `align_up` | `(size: i32, alignment: i32) -> i32` |
| `align_down` | `(size: i32, alignment: i32) -> i32` |
| `memory_check` | `(ptr: i32, size: i32) -> bool` |
| `memory_check_write` | `(ptr: i32, size: i32) -> bool` |
| `memory_fill_pattern` | `(ptr: i32, pattern: i32, count: i32) -> i32` |
| `memory_zero` | `(ptr: i32, size: i32) -> i32` |
| `memory_copy_nonoverlapping` | `(dest: i32, src: i32, n: i32) -> i32` |
| `memory_copy_overlapping` | `(dest: i32, src: i32, n: i32) -> i32` |
| `alloca` | `(size: i32) -> i32` |
| `stack_array_i32` | `(count: i32) -> i32` |
| `stack_array_f32` | `(count: i32) -> i32` |
| `memory_pool_create` | `(size: i32) -> MemoryPool` |
| `memory_pool_alloc` | `(pool: MemoryPool, size: i32, alignment: i32) -> i32` |
| `memory_pool_reset` | `(pool: MemoryPool) -> i32` |
| `memory_pool_destroy` | `(pool: MemoryPool) -> i32` |
| `memory_dump` | `(ptr: i32, size: i32, bytes_per_line: i32) -> i32` |
| `memory_validate` | `(ptr: i32, size: i32) -> bool` |
| `format_hex` | `(value: i32) -> string` |
| `format_hex_ptr` | `(ptr: i32) -> string` |

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

| Name | Signature |
|------|-----------|
| `net2x2x1_param_get` | `(net: Net2x2x1, idx: i32) -> f32` |
| `net2x2x1_param_set` | `(net: Net2x2x1, idx: i32, value: f32) -> Net2x2x1` |
| `net2x2x1_grad_get` | `(g: Grads2x2x1, idx: i32) -> f32` |
| `net2x2x1_predict` | `(net: Net2x2x1, x0: f32, x1: f32) -> f32` |
| `net2x2x1_loss_xor` | `(net: Net2x2x1) -> f32` |
| `net2x2x1_grads_xor` | `(net: Net2x2x1) -> Grads2x2x1` |
| `net2x2x1_step` | `(net: Net2x2x1, grads: Grads2x2x1, lr: f32) -> Net2x2x1` |
| `net2x2x1_gradcheck_xor` | `(net: Net2x2x1, eps: f32) -> f32` |
| `net2x4x1_predict` | `(net: Net2x4x1, x0: f32, x1: f32) -> f32` |
| `net2x4x1_loss_xor` | `(net: Net2x4x1) -> f32` |
| `net2x4x1_grads_xor` | `(net: Net2x4x1) -> Grads2x4x1` |
| `net2x4x1_step` | `(net: Net2x4x1, grads: Grads2x4x1, lr: f32) -> Net2x4x1` |
| `net2x8x1_predict` | `(net: Net2x8x1, x0: f32, x1: f32) -> f32` |
| `net2x8x1_loss_xor` | `(net: Net2x8x1) -> f32` |
| `net2x8x1_grads_xor` | `(net: Net2x8x1) -> Grads2x8x1` |
| `net2x8x1_step` | `(net: Net2x8x1, grads: Grads2x8x1, lr: f32) -> Net2x8x1` |

### `nn_autogen.flow`

Auto-generated backprop for XOR loss (2x2x1) via scripts/tools/grad/flow_grad_flow.py  This file demonstrates "no hand-written backprop": gradients are generated from

**Functions:**

| Name | Signature |
|------|-----------|
| `net2x2x1_grads_xor_autogen` | `(net: Net2x2x1) -> Grads2x2x1` |

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

| Name | Signature |
|------|-----------|
| `run_cmd` | `(cmd: string) -> i32` |
| `have_cmd` | `(name: string) -> bool` |
| `env_is` | `(name: string, want: string) -> bool` |
| `str_eq` | `(a: string, b: string) -> bool` |

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

| Name | Signature |
|------|-----------|
| `python_init_or_print` | `() -> bool` |
| `python_add_paths` | `(p1: string, p2: string) -> i32` |
| `python_import_or_null` | `(name: string) -> ptr<void>` |
| `python_call0_or_print` | `(py_mod: ptr<void>, fn_name: string) -> i32` |
| `python_call1_str_or_print` | `(py_mod: ptr<void>, fn_name: string, arg: string) -> i32` |
| `python_call1_i32_or_print` | `(py_mod: ptr<void>, fn_name: string, arg: i32) -> i32` |
| `python_call1_f32_or_print` | `(py_mod: ptr<void>, fn_name: string, arg: f32) -> i32` |
| `python_call1_bool_or_print` | `(py_mod: ptr<void>, fn_name: string, arg: bool) -> i32` |
| `python_begin` | `(p1: string, p2: string) -> PythonContext` |
| `python_import` | `(ctx: PythonContext, name: string) -> PythonContext` |
| `python_call` | `(ctx: PythonContext, fn_name: string) -> PythonContext` |
| `python_call_str` | `(ctx: PythonContext, fn_name: string, arg: string) -> PythonContext` |
| `python_call_i32` | `(ctx: PythonContext, fn_name: string, arg: i32) -> PythonContext` |
| `python_call_f32` | `(ctx: PythonContext, fn_name: string, arg: f32) -> PythonContext` |
| `python_call_bool` | `(ctx: PythonContext, fn_name: string, arg: bool) -> PythonContext` |
| `python_end` | `() -> void` |

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

| Name | Signature |
|------|-----------|
| `rect` | `(x: f32, y: f32, w: f32, h: f32, r: i32, g: i32, b: i32, a: i32) -> void` |
| `circle` | `(x: f32, y: f32, radius: f32, r: i32, g: i32, b: i32, a: i32) -> void` |
| `group` | `() -> void` |
| `end_group` | `() -> void` |
| `transform` | `(tx: f32, ty: f32, sx: f32, sy: f32, rot: f32) -> void` |
| `end_transform` | `() -> void` |
| `render` | `(filename: string, width: i32, height: i32) -> void` |

### `string.flow`

FLOW String Utilities

*No `export` items found (internal / extern-only module).*

### `sys_info.flow`

System information helpers (extern-backed)

**Functions:**

| Name | Signature |
|------|-----------|
| `os_name` | `() -> string` |
| `cpu_name` | `() -> string` |
| `cpu_arch` | `() -> string` |
| `cpu_cores` | `() -> i32` |
| `cpu_features_string` | `() -> string` |

### `tensor.flow`

Tensor: N-dimensional array type for neural networks (stdlib) Import: import "stdlib/tensor.flow" MLIR-first ML workloads: use with `flow ml` or `flow mlir-run`

*No `export` items found (internal / extern-only module).*

### `time.flow`

**Functions:**

| Name | Signature |
|------|-----------|
| `get_time` | `() -> f64` |

### `ui.flow`

FLOW Terminal UI Helpers  Minimal, dependency-free helpers for building text UIs.

**Functions:**

| Name | Signature |
|------|-----------|
| `ui_clear` | `() -> void` |
| `ui_hide_cursor` | `() -> void` |
| `ui_show_cursor` | `() -> void` |
| `ui_reset_style` | `() -> void` |
| `ui_bold_on` | `() -> void` |
| `ui_dim_on` | `() -> void` |
| `ui_fg` | `(code: i32) -> void` |
| `ui_bg` | `(code: i32) -> void` |
| `ui_newline` | `() -> void` |
| `ui_flush` | `() -> void` |
| `ui_print_spaces` | `(n: i32) -> void` |
| `ui_read_char` | `() -> i32` |
| `ui_read_non_newline_char` | `() -> i32` |
| `ui_consume_line` | `() -> void` |

### `ui2d.flow`

UI2D: tiny immediate-mode 2D drawing on SDL2  This is “graphics library written in FLOW”: rectangles + a built-in bitmap

**Functions:**

| Name | Signature |
|------|-----------|
| `ui2d_init` | `(title: string, w: i32, h: i32) -> Ui2D` |
| `ui2d_shutdown` | `(ui: Ui2D) -> void` |
| `ui2d_poll` | `(ui: Ui2D) -> Ui2D` |
| `ui2d_key_down` | `(scancode: i32) -> bool` |
| `ui2d_begin` | `(ui: Ui2D, clear: Color) -> void` |
| `ui2d_end` | `(ui: Ui2D) -> void` |
| `ui2d_fill_rect` | `(ui: Ui2D, x: i32, y: i32, w: i32, h: i32, c: Color) -> void` |
| `ui2d_draw_digit` | `(ui: Ui2D, x: i32, y: i32, d: i32, scale: i32, c: Color) -> void` |
| `ui2d_draw_number` | `(ui: Ui2D, x: i32, y: i32, n: i32, scale: i32, c: Color) -> void` |

### `ui_layout.flow`

Simple UI layout helpers for DSL blocks

**Structs:** `UiRect`, `UiLayoutFrame`, `UiLayoutState`

**Constants:**

- `UI_JUSTIFY_START: i32`
- `UI_JUSTIFY_CENTER: i32`
- `UI_JUSTIFY_END: i32`

**Functions:**

| Name | Signature |
|------|-----------|
| `ui_layout_set_view` | `(state: ptr<UiLayoutState>, win_w: f32, win_h: f32) -> void` |
| `ui_next_rect` | `(state: ptr<UiLayoutState>) -> UiRect` |
| `ui_layout_begin` | `(state: ptr<UiLayoutState>, cols: i32, rows: i32, pad: i32) -> void` |
| `ui_layout_end` | `(state: ptr<UiLayoutState>) -> void` |
| `ui_row_begin` | `(state: ptr<UiLayoutState>, cols: i32, gap: i32, pad: i32, justify: i32) -> void` |
| `ui_row_end` | `(state: ptr<UiLayoutState>) -> void` |
| `ui_column_begin` | `(state: ptr<UiLayoutState>, rows: i32, gap: i32, pad: i32, justify: i32) -> void` |
| `ui_column_end` | `(state: ptr<UiLayoutState>) -> void` |
| `ui_grid_begin` | `(state: ptr<UiLayoutState>, cols: i32, rows: i32, gap: i32, pad: i32, justify_x: i32, justify_y: i32) -> void` |
| `ui_grid_end` | `(state: ptr<UiLayoutState>) -> void` |
| `ui_stack_begin` | `(state: ptr<UiLayoutState>) -> void` |
| `ui_stack_end` | `(state: ptr<UiLayoutState>) -> void` |
| `ui_box` | `(state: ptr<UiLayoutState>) -> UiRect` |

### `vec.flow`

Flow Standard Library: Vector Types Built-in Vec2/Vec3 with operator overloading

*No `export` items found (internal / extern-only module).*

### `vulkan.flow`

Vulkan Flow wrapper (macOS + MoltenVK demo bridge)

**Functions:**

| Name | Signature |
|------|-----------|
| `vulkan_run_basic` | `(opts: VulkanOptions) -> i32` |
| `vulkan_run_advanced` | `(opts: VulkanOptions) -> i32` |
| `vulkan_run_basic_with_config` | `(opts: VulkanOptions, cfg: VulkanConfig) -> i32` |
| `vulkan_run_advanced_with_config` | `(opts: VulkanOptions, cfg: VulkanConfig) -> i32` |

### `vulkan_abi_renderer.flow`

**Functions:**

| Name | Signature |
|------|-----------|
| `abi_renderer_init` | `() -> AbiRenderer` |
| `abi_renderer_begin_frame` | `(r: AbiRenderer) -> i32` |
| `abi_renderer_end_frame` | `(r: AbiRenderer) -> void` |
| `abi_renderer_create_instance_buffer` | `(r: AbiRenderer, capacity: i32) -> i32` |
| `abi_renderer_update_instance_buffer` | `(r: AbiRenderer, buf: i32, instance_data: ptr<f32>, count: i32) -> void` |
| `abi_renderer_draw_instance_buffer` | `(r: AbiRenderer, buf: i32, count: i32) -> void` |
| `abi_renderer_create_texture` | `(r: AbiRenderer, width: i32, height: i32) -> i32` |
| `abi_renderer_update_texture` | `(r: AbiRenderer, tex: i32, pixels: ptr<u8>, width: i32, height: i32) -> void` |
| `abi_renderer_upload_mesh` | `(r: AbiRenderer, vertices: ptr<f32>, vertex_count: i32, indices: ptr<u16>, index_count: i32) -> void` |
| `abi_renderer_set_clear` | `(r: AbiRenderer, r_col: f32, g_col: f32, b_col: f32) -> void` |
| `abi_renderer_set_camera` | `(r: AbiRenderer, distance: f32, pitch: f32, yaw: f32) -> void` |
| `abi_renderer_set_viewport` | `(r: AbiRenderer, width: i32, height: i32) -> void` |
| `abi_renderer_set_window_scale` | `(r: AbiRenderer, scale: f32, force_square: bool) -> void` |

### `vulkan_renderer.flow`

**Functions:**

| Name | Signature |
|------|-----------|
| `renderer_basic` | `() -> Renderer` |
| `renderer_advanced` | `() -> Renderer` |
| `renderer_set_clear` | `(r: Renderer, r_col: f32, g_col: f32, b_col: f32) -> Renderer` |
| `renderer_set_window` | `(r: Renderer, w: i32, h: i32, title: string) -> Renderer` |
| `renderer_set_texture` | `(r: Renderer, path: string) -> Renderer` |
| `renderer_set_texture2` | `(r: Renderer, path: string) -> Renderer` |
| `renderer_pick_texture` | `(r: Renderer) -> Renderer` |
| `renderer_pick_texture2` | `(r: Renderer) -> Renderer` |
| `renderer_set_camera` | `(r: Renderer, distance: f32, pitch: f32, yaw: f32) -> Renderer` |
| `renderer_set_camera_speed` | `(r: Renderer, move_speed: f32, mouse_sensitivity: f32) -> Renderer` |
| `renderer_set_camera_smoothing` | `(r: Renderer, smoothing: f32) -> Renderer` |
| `renderer_set_material1` | `(r: Renderer, r_col: f32, g_col: f32, b_col: f32) -> Renderer` |
| `renderer_set_material2` | `(r: Renderer, r_col: f32, g_col: f32, b_col: f32) -> Renderer` |
| `renderer_set_instances` | `(r: Renderer, count: i32) -> Renderer` |
| `renderer_set_trace` | `(r: Renderer, trace_on: bool) -> Renderer` |
| `renderer_set_validation` | `(r: Renderer, validation_on: bool) -> Renderer` |
| `renderer_run` | `(r: Renderer) -> i32` |

