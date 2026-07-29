# Audio DSP Standard Library

Flow ships with a pragmatic audio DSP layer focused on real-time routing and effects.

> [!important] Real-time contract
> Nothing on the audio thread may allocate or block. See **[RT Safety Policy](rt-safety.md)** for the allowed / forbidden checklist (prep vs process).

## Modules

- `stdlib/audio.flow`  
  Core types: `SampleRate`, `Frame`, `AudioBufferF32`, time helpers.
- `stdlib/audio/filters.flow`  
  One-pole, DC blocker, and biquad filters.
- `stdlib/audio/delay_line.flow`  
  Real delay line with ring buffer storage.
- `stdlib/audio/graph.flow`  
  High-level effect chain (gain, lowpass, delay, pan) with update helpers.
- `stdlib/audio/graph_scheduler.flow`  
  Fixed-size node graph scheduler for block processing.
- `stdlib/audio/graph_bus.flow`  
  Bus-based graph for parallel routing and mixing.
- `stdlib/audio/control.flow`  
  Control-rate smoothing utilities.
- `stdlib/audio/io.flow`  
  Real-time audio I/O API (backend in `runtime/`).
- `stdlib/audio/gpu.flow`  
  GPU acceleration (Metal on macOS, CPU fallback).
- `stdlib/audio/simd.flow`  
  CPU SIMD-friendly helpers.
- `stdlib/audio/live.flow`  
  Single-standard live graph (one buffer layout + plugin ABI).

## Real-time I/O Backend (Cross-platform)

The I/O API uses a push/pull ring-buffer design so Flow code does not need function pointers.
To enable real-time audio, compile with a backend implementation:

### Miniaudio (Recommended)
`third_party/miniaudio.h` is bundled. The CLI will auto-enable it when present.
To compile manually, include:
- `runtime/audio_miniaudio.c`
- `-DFLOW_AUDIO_BACKEND_MINIAUDIO`
- `-Ithird_party`

If `miniaudio.h` is not present, the backend compiles as a stub and will not open devices.

Example build (macOS/Linux):
```bash
clang -O2 build/your_program.c runtime/audio_miniaudio.c runtime/audio_simd.c -Ithird_party -o build/your_program
```

On macOS, the CLI links Metal automatically when using `./flow audio`.

### Using the CLI
```bash
./flow audio examples/audio/loopback_effects.flow
```

### Device Probe
Use `audio_probe_devices()` to print a quick device count via the backend.

## Live Standard
The live graph standardizes on:
- Interleaved `f32` buffers
- A single graph API (`live_graph_*`)
- A single plugin ABI (`flow_live_plugin_*`)

Hot-swap support is provided via `LiveGraphHandle` in `stdlib/audio/live.flow`.

## Example
See `examples/audio/loopback_effects.flow` for input -> effect chain -> output,
`examples/audio/offline_graph_demo.flow` / `examples/audio/bus_graph_demo.flow` for offline graph processing,
and `examples/audio/gpu_gain_demo.flow` for GPU (fallback) processing.

## Control Rate
Control parameters are applied per-sample and intended to be smoothed using filters
from `audio/filters.flow` (e.g., `onepole_smooth`) when needed.
