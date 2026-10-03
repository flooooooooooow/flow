# Denotational MLIR for Flow evolution blocks

> Status: design only. Nothing here is implemented in flowc yet. A prototype
> emitter was written in Python (`src/flow/denotational_mlir.py`) against the
> Python compiler. That compiler and its MLIR generator are retired, and the
> prototype never merged. Its code is kept at the tag
> `archive/feat/denotational-mlir` (see [archive tags](../project/archive-tags.md)).
> The `flow.*` dialect described here is a future slice for the Flow MLIR
> emitter, [`compiler/src/mlirgen.flow`](../../compiler/src/mlirgen.flow).
> Related MLIR optimization issues: #664, #665, #667, #671.

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

flowc desugars this in
[`compiler/src/flow_blocks.flow`](../../compiler/src/flow_blocks.flow) to plain
Flow functions (`Pendulum_step`, a factored `Pendulum_derivs`, `Pendulum_new`,
`Pendulum_init`, `Pendulum_outputs`) that every backend, MLIR included, then
lowers. That is correct and shipped. The cost is that the denotation is gone by
the time MLIR sees it: `Pendulum_derivs` is an opaque function. The MLIR
optimization work cannot see that this is a vector field, so it cannot batch,
fuse or vectorize an ensemble of `Pendulum` instances into one stepped kernel.
The issues that would use it:

- #664, value semantics and one-shot bufferization,
- #665, polyhedral loop transformations through the affine and linalg dialects,
- #667, automatic memory layout transformations (AoSoA and conflict padding),
- #671, dynamic shape specialization and JIT kernel synthesis (closed).

## The denotation to preserve

An evolution block denotes a first-order system

    dx/dt = f(x, u, p),   x in state, u in input, p in param

plus a discrete overlay: `every` blocks apply periodic `becomes` updates, and
`when x reaches L` applies zero-crossing resets. The integration method (Euler,
RK4) is a lowering choice that sits outside the denotation. The step ordering
is fixed by the spec: integrate, `every`, events, outputs.

The MLIR representation should carry `f` structurally so a pass can:

- prove `f` is pure and elementwise across an ensemble, then fuse the
  derivative evaluations of N instances into one vectorized region (#665),
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
  derivative (the same check `flow_blocks.flow` makes).
- `flow.every <duration_ns> { flow.becomes %x = <region> }`: periodic updates.
- `flow.when <region> reaches <region> { flow.becomes %x = <region> }`:
  zero-crossing events.
- `flow.step %sys, %dt`: one integration step of a system value. This is the
  lowering hook where a method (Euler or RK4) and an ensemble strategy are
  chosen.

`flow.evolve` bodies use `arith`/`math` for the expression subset so ordinary
canonicalization already applies inside a derivative.

## Lowering pipeline

1. flowc emits `flow.system` with `flow.evolve`/`flow.every`/`flow.when` from
   the parsed flow block, before the `flow_blocks.flow` desugaring runs.
2. An ensemble pass rewrites `flow.step` over an array of systems into a fused,
   vectorized region when every `flow.evolve` body is pure and elementwise.
3. Everything not fused lowers to the existing plain-function form, so the C
   backend and the unoptimized MLIR path stay byte for byte as today. The
   denotational lane is an optimization opportunity and never changes what a
   program computes.

## What the Python prototype covered

The archived prototype is a starting point for the Flow slice. It emitted the
`flow.system` dialect from a parsed flow block:

- `flow.state`/`flow.param` members with their declared initializers,
- one `flow.evolve` region per state, with the derivative lowered to
  `arith`/`math` for the supported subset and kept as `flow.opaque` otherwise,
- `flow.every <period_ns> { flow.becomes ... }` for periodic resets,
- `flow.when %x reaches { ... } do { flow.becomes ... }` for zero-crossing
  events.

Member kinds it did not cover (always/never invariants, solver, connections,
child systems) were flagged with a `flow.pending` op so partial output is never
taken for the whole system. Its tests ran against the pendulum, thermostat and
bouncing-ball examples.

It also prototyped the ensemble payoff: `flow.ensemble @Name x N`, where each
state and param is a `vector<Nxf64>` and every `flow.evolve` body runs the same
`arith`/`math` ops over the whole ensemble, so N systems step in one kernel
(checked on 1000 pendulums). Per-instance `every`/`when` resets stayed on the
scalar path and were flagged `flow.pending`. This is the transformation the
opaque `_derivs` call blocks.

## The Flow slice

The work that remains, in order:

1. Port the textual emitter into `compiler/src/mlirgen.flow` as a pass over flow
   blocks that writes the `flow.*` module ahead of the operational lowering,
   behind an opt-in switch (the prototype used `FLOW_DENOTATIONAL=1`). Default
   output stays unchanged, so `compiler/scripts/mlir_vs_c.flow` and the MLIR
   goldens hold.
2. Add the fused ensemble step as a second opt-in output.
3. Run the ensemble fusion as a real `mlir-opt` pass that consumes the dialect,
   in place of a textual rewrite, once the dialect shape is agreed with the
   MLIR optimization work above.

See also [MLIR in Flow](mlir-in-flow.md), which records the port of the MLIR
backend from Python to Flow.
