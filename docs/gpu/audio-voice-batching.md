# GPU voice-batch synthesis (experimental)

Flow can already lower a subset of `@gpu` functions to GPU code, but its
existing `stdlib/audio/gpu.flow` is not a polyphonic GPU synthesizer.
This experiment is a concrete first step: **one stateful resonator per GPU
thread**, an ordered time loop *inside* each voice, a separate mix pass,
and persistent state across consecutive blocks.

## Reproduce the executable parity case

```sh
./flow gpu-lower tests/gpu_lower/kernels/modal_bank.flow --target metal --run --ulp 0
./flow tool tests/gpu_lower/run.flow --only modal_bank
```

The Flow source is
[`tests/gpu_lower/kernels/modal_bank.flow`](../../tests/gpu_lower/kernels/modal_bank.flow).
The CPU reference and GPU version use the same `@gpu` kernels. The CPU
harness independently proves cross-block behaviour before any device
comparison:

- an unsplit 128-sample recurrence for voice 0 must match both the
  mid-block state (after 64 samples) and the final state (after 128);
- block 0 must mutate state away from the initial excitation, and block 1
  must mutate it further rather than replaying block 0;
- distinct coefficients must leave voice 0 and voice 1 in different final
  states;
- the first sample of block 1 must equal the recurrence step from the
  mid-block SoA state (continuity across the dispatch boundary).

The `gpu-lower` harness then checks the device's intermediate state and
both blocks of per-voice and mixed samples against that reference. In
environments without a GPU/toolchain, runnable targets are SKIP; PTX and
HSACO generation still exercise lowering. SKIP is not evidence of device
parity.

A voice is a second-order resonator with coefficients prepared on the CPU:

```text
y[n] = a[voice] * y[n-1] + b[voice] * y[n-2]
partial[frame, voice] = gain[voice] * y[n]
mix[frame] = sum_voice partial[frame, voice]
```

Two state arrays (`prev`, `older`) are **structures of arrays**, not
one allocated object per voice. The coefficients and gains are separate
arrays. The output partials are sample-major, so adjacent GPU threads
write adjacent float samples at a given instant. The independent
`mix_modes` dispatch reads those partials and returns only one sample
per frame to the host. This specific reduction is a correctness
reference, not a scalable production reduction for tens of thousands
of voices.

```text
CPU: configure modes        GPU: render block 0          GPU: mix block 0
                              state A -> B
CPU: reuse state B          GPU: render block 1          GPU: mix block 1
                              state B -> C
CPU: consume stereo mix / run single-instance DSP and I/O
```

The prototype uses two distinct state-buffer pairs so it also works
with GPU runners that forbid in-place output, including the MLX parity
runner. A production synthesizer should use persistent buffers and
double-buffer state across calls, not rebuild the runner or serialize
through the test fixture.

## Why batching is essential

A recursive oscillator or filter has a loop-carried dependency:
sample `n + 1` depends on sample `n`. Splitting a **single** voice
across many GPU threads is generally unhelpful. Splitting **many
independent voices** across GPU threads preserves the recurrence and
amortizes dispatch. This is the relevant insight from
[Faust's Mojo GPU synthesis study](https://github.com/grame-cncm/faust-rs/blob/main/docs/mojo-gpu-synthesis-en.md).

Faust's reported speedups and latency were measured on its implementation
and hardware. They are **not Flow benchmarks**. This prototype claims only
a portable lowering/parity target, pending verification on GPU hardware.

## Required production follow-ups

This test is deliberately **not** a real-time instrument yet.

A production implementation needs a Flow-native, typed voice/parameter
description and a lowering path that specialises a single voice into
batched GPU kernels. The current GPU emitter subset has limited math
functions and no general automatic state promotion or arbitrary DSP
lowering. Delay-line state needs distinct treatment from register-suitable
scalar recurrence.

The runtime needs resident kernels and state buffers, control updates
without per-block compilation or allocation, multi-level GPU reductions
for very large voice counts, bounded command submissions, and deterministic
CPU fallback. The audio callback must **never** wait for a GPU fence:
a separate worker should render ahead into a bounded single-producer,
single-consumer block queue. Measure end-to-end latency, underruns,
p99.9 block time, GPU wake-up jitter, and power at 64/128/256/512 frames;
do not infer safety from average GPU execution time.

Compare against a **well-optimised CPU structure-of-voices** baseline,
not just a CPU interpreter of GPU-oriented storage. Add offline modal
fitting and differentiable DSP only after the synthesis path is correct.

## Gate 1a: other voices, variable blocks, parameter updates

[`tests/gpu_lower/kernels/voice_osc_varblocks.flow`](../../tests/gpu_lower/kernels/voice_osc_varblocks.flow)
covers the next correctness slice after the modal bank:

```sh
./flow tool tests/gpu_lower/run.flow --only voice_osc_varblocks
```

- **Other voice program:** 64 independent phase-accumulator oscillators
  (SoA phase, frequency and gain), not resonators.
- **Variable block sizes:** block 0 is 48 frames; block 1 is 80 frames,
  with separate frame scalars and differently sized partial/mix buffers.
- **Mid-stream parameter updates:** block 1 binds new frequency and gain
  buffers while continuing from the mid-block phase.
- **Negative checks in `main()`:** returns nonzero if phase is reset to
  the initial excitation between dispatches, if block 1 is replayed with
  the old length and coefficients, or if the first sample of block 1
  matches a reset-from-init formula under the new parameters.

Phase wrap and delay-line topologies remain separate follow-ups (they need
`if`-assigned locals inside GPU loops). One-pole / biquad banks and
Karplus-Strong are covered by companion PRs under the same epic.

## Current constraints

The modal bank remains a fixed two-block, mono test with 128 modes and
64 frames/block. The oscillator case above varies block length and
parameters but still has no file I/O, allocations, transcendentals or
effects. Both compile through the existing `gpu-lower` harness; neither
is yet a dispatchable callback-based audio library. Native
`audio/gpu.flow` contains other experimental Metal routines and should
not be conflated with this execution model.
