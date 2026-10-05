# Audio Examples

## rt_safe_callback.flow
Minimal `@rt_safe` process block — stack locals and fixed-bound loops only.
Compile-time checker rejects heap calls from `@rt_safe` (see `docs/library/rt-safety.md`).

```bash
./flow run examples/audio/rt_safe_callback.flow
```

## lattice_allpass_phase_engine.flow
Larger `@rt_safe` DSP demo (Schur lattice phase engine).

## loopback_effects.flow
Real-time input -> effect chain -> output loopback.

Requires the audio runtime backend configured (see `docs/library/audio.md`).

## offline_graph_demo.flow
Offline graph processing demo (no audio device required).

## bus_graph_demo.flow
Parallel bus routing demo (offline).

## gpu_gain_demo.flow
GPU gain demo (falls back to CPU if GPU unavailable).
