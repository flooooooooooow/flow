# Denotational MLIR for Flow evolution blocks

> Status: design + prototype. The prototype lives in `src/flow/denotational_mlir.py`
> with tests in `tests/unit/test_denotational_mlir.py`. This document is the plan
> the prototype implements a first slice of. It coordinates with the MLIR
> optimization work on the `flow.*` dialect (issues #664, #665, #667, #671).

## Problem

A `flow` block is Flow's denotational core: it states how a system evolves in
time rather than how to compute a step.

```flow
flow Pendulum {
    state angle: f64 = 0.2
    state velocity: f64 = 0.0
    param gravity: f64 = 9.81
    param length: f64 = 1.0

    angle evolves as velocity
    velocity evolves as -(gravity / length) * sin(angle)
}
```

Today `src/flow/flow_blocks.py` desugars this to plain Flow functions
(`Pendulum_step`, a factored `Pendulum_derivs`, `Pendulum_new`, `Pendulum_init`,
`Pendulum_outputs`) that every backend, including MLIR, then lowers. That is
correct and shipped (north-star `evolves-syntax` card). The cost is that the
denotation is gone by the time MLIR sees it: `Pendulum_derivs` is an opaque
function. The MLIR passes that are landing, elementwise fusion (#665), AoSoA
layout (#667), one-shot bufferization (#664) and shape specialization (#671),
cannot see that this is a vector field, so they cannot batch, fuse or vectorize
an ensemble of `Pendulum` instances into one stepped kernel.

## The denotation to preserve

An evolution block denotes a first-order system

    dx/dt = f(x, u, p),   x in state, u in input, p in param

plus, from the shipped cards, a discrete overlay: `every` blocks apply periodic
`becomes` updates, and `when x reaches L` applies zero-crossing resets. The
integration method (Euler, RK4) is a lowering choice that sits outside the
denotation. The step ordering is fixed by the spec: integrate, `every`, events,
outputs.

The MLIR representation should carry `f` structurally so a pass can:

- prove `f` is pure and elementwise across an ensemble, then fuse the derivative
  evaluations of N instances into one vectorized region (connects to #665),
- choose an AoSoA layout for the ensemble state (#667),
- specialize on a statically known ensemble size (#671).

## Proposed `flow` dialect ops

A denotational lane that sits above the current desugaring, lowered to the same
plain functions when no ensemble optimization applies:

- `flow.system @Name { ... }`: a region holding the members of one block.
- `flow.state %x : f64 = <init>` and `flow.param %p : f64 = <init>`: named
  members with their declared defaults.
- `flow.evolve %x = <region>`: the derivative of one state. The region is a
  pure expression over the system's states, inputs and params, terminated by
  `flow.deriv <ssa>`. One `evolve` per state, and a state has exactly one
  derivative (this matches the flow_blocks.py check).
- `flow.every <duration_ns> { flow.becomes %x = <region> }`: periodic updates.
- `flow.when <region> reaches <region> { flow.becomes %x = <region> }`:
  zero-crossing events.
- `flow.step %sys, %dt`: one integration step of a system value. This is the
  lowering hook where a method (Euler or RK4) and an ensemble strategy are
  chosen.

`flow.evolve` bodies use `arith`/`math` for the expression subset so ordinary
canonicalization already applies inside a derivative.

## Lowering pipeline

1. Front end emits `flow.system` with `flow.evolve`/`flow.every`/`flow.when`
   from `FlowDecl`, before the flow_blocks.py desugaring runs.
2. An ensemble pass rewrites `flow.step` over an array of systems into a fused,
   vectorized region when every `flow.evolve` body is pure and elementwise.
3. Everything not fused lowers to the existing plain-function form, so the C
   backend and the un-optimized MLIR path stay byte-for-byte as today. The
   denotational lane is an optimization opportunity, never a correctness change.

## First slice (this prototype)

`src/flow/denotational_mlir.py` emits the `flow.system` dialect from a parsed
`FlowDecl`, covering all three shipped cards:

- `flow.state`/`flow.param` members with their declared initializers,
- one `flow.evolve` region per state, with the derivative lowered to
  `arith`/`math` for the supported subset and kept as `flow.opaque` otherwise,
- `flow.every <period_ns> { flow.becomes ... }` for periodic resets,
- `flow.when %x reaches { ... } do { flow.becomes ... }` for zero-crossing
  events.

Member kinds this emitter does not yet cover (always/never invariants, solver,
connections, child systems) are flagged with a `flow.pending` op so partial
output is never taken for the whole system. It is a textual emitter that
documents the dialect shape, exercised by `tests/unit/test_denotational_mlir.py`
against the pendulum, thermostat and bouncing-ball examples.

The ensemble-fusion payoff is prototyped too: `emit_ensemble_step(flow, n)`
emits `flow.ensemble @Name x N` where each state and param is a
`vector<Nxf64>` and every `flow.evolve` body runs the same `arith`/`math` ops
over the whole ensemble, so N systems step in one kernel (verified on 1000
pendulums). Per-instance `every`/`when` resets stay on the scalar path and are
flagged `flow.pending`. This is the transformation the opaque `_derivs` call
blocks, and it connects directly to the fusion (#665) and AoSoA (#667) passes.

The emitter is wired into the real compiler front end as an opt-in flag on
`flow.transpiler`:

```sh
python -m flow.transpiler pendulum.flow --emit-denotational-mlir       # flow.system
python -m flow.transpiler pendulum.flow --emit-denotational-mlir 1000  # fused ensemble
```

This runs on the raw `FlowDecl`s before the flow_blocks.py desugaring, so it
needs no change to `mlir_generator.py`, and normal compilation is byte-for-byte
unchanged (it is a new argument and an early-exit branch that mirror the
existing `--print-pass-pipeline` path). `scripts/emit_denotational_mlir.py` is
the same capability as a standalone script.

The deeper integration remains for later, once the dialect shape is agreed with
the MLIR work: producing `flow.*` inside the normal MLIR lowering and running
the ensemble fusion as a real `mlir-opt` pass rather than a textual emitter.
That step touches `mlir_generator.py`, which is under active edit, so it is
sequenced after this lane is reviewed.

## Coordination

`mlir_generator.py`, `dynamics_dsl.flow` and the MLIR passes are under active
edit. This lane is deliberately a new module plus a design doc, touching no file
in that set, so it can land without conflict and be wired in once the dialect
shape is settled. See the note in `AGENTS.md`.
