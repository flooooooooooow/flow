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
The CPU reference and GPU version use the same `@gpu` kernels, with a
second, unsplit CPU recurrence checking that the second block continues
rather than restarting the oscillation. The `gpu-lower` harness checks the
device's intermediate state and both blocks of per-voice and mixed samples
against that reference. In environments without a GPU/toolchain, targets
are SKIP, not evidence of GPU parity.

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

## Current constraints

This is a fixed two-block, mono test with 128 modes and 64 frames/block.
The kernel contains no file I/O, allocations, transcendentals or effects.
The source is compiled through the existing `gpu-lower` harness; it is
not yet a dispatchable callback-based audio library. Native `audio/gpu.flow`
contains other experimental Metal routines and should not be conflated
with this execution model.
