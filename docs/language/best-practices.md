# Coding best practices

How to write Flow that stays clear as it grows, and why the language pushes you
toward fluid, abstract programs instead of step-by-step machine recipes.

This is not a second language spec. For syntax and semantics see the
[overview](overview.md) and [LANGUAGE_SPEC](../LANGUAGE_SPEC.md). For the product
thesis see [Vision](../vision.md) and [VISION.md](../../VISION.md).

## Why Flow wants fluid abstraction

Most languages ask you to narrate *instructions*: allocate, update, call, loop.
Flow's thesis is that you should narrate *behavior*: what exists, how it
evolves, what it may touch, and what must stay true.

That shows up in the surface:

| Instead of… | Prefer… |
|---|---|
| A manual RK4 loop with scratch arrays | A `flow` block with `evolves as` and a solver |
| Passing logger / clock / DB through every signature | An `effect` + `handle` at the edge |
| Hand-written gradients | Stdlib autodiff / checked-in grad for the model |
| `ptr + length` that can lie | `span<T>` (or an honest array + length stand-in while learning) |
| Nested temps for transforms | `|>` pipelines with `_` where the value is not first |

Fluid here does not mean sloppy. Types, effects, and (where used) units and
`always` constraints are how abstraction stays cheap and checkable. The C
backend keeps the escape hatch: when you need a tight loop or FFI, you drop
down without leaving the language.

The payoff is one description that can be simulated, analyzed, trained against,
and deployed, instead of a Python notebook, a MATLAB controller, and a C port
that drift apart. See [Vision](../vision.md).

## Defaults that age well

### Prefer names that say what evolves

Name state after the physical or domain thing (`angle`, `inventory`, `frame`),
not after the buffer (`buf2`, `tmp`). In `flow` blocks and `dsys` models, the
name *is* the interface to analysis and codegen.

```flow
flow Spring {
    state x: f64 = 0.0
    state v: f64 = 0.0
    param k: f64 = 4.0
    param m: f64 = 1.0

    x evolves as v
    v evolves as -(k / m) * x
}
```

### Keep `let` immutable until mutation is the point

Use `let mut` only for real accumulators and in-place updates. Immutable
bindings make pipelines and effectful code easier to follow.

### Put types on the public edge

Annotate function parameters, returns, and struct fields. Inference is fine
inside small bodies; the API surface should stay readable without a language
server.

### Small functions, obvious data

Prefer short functions that transform one idea over long procedures that mix
I/O, math, and policy. Structs and arrays carry the data; effects carry the
world.

## Composition: pipelines and transforms

Thread values with `|>`. Use `_` when the piped value is not the first
argument. Declare sort intent with `|> sort` / `sortBy` when order is part of
the meaning, not an accident of the loop.

```flow
function clamp(lo: i32, x: i32, hi: i32) -> i32 {
    if x < lo { return lo }
    if x > hi { return hi }
    return x
}

function main() -> i32 {
    let v: i32 = 150 |> clamp(0, _, 100)
    printf("%d\n", v)
    return 0
}
```

Practice: [pipelines tutorial](../tutorials/pipelines.md) ·
`examples/basics/pipeline_placeholder.flow`.

Avoid building deep call chains that hide side effects. Pure transforms in the
middle; effects at the rim.

## Effects: abstract the world, not the business logic

Write domain logic against effect interfaces. Install handlers at the boundary
(tests, prod, null, file). Do not thread `Logger` / `Clock` / `Store` through
every call as parameters unless the function is itself a handler.

```flow
effect Log {
    info(msg: string) -> void
}

function charge(amount: i32) -> i32 {
    Log.info("charge")
    return amount
}
```

Then `handle Log with { ... } in { charge(10) }` at the edge.

Rules of thumb:

1. One effect per capability (log, time, inventory), not one mega-effect.
2. Handlers should be boring: no domain policy inside the logger.
3. Tests swap handlers; they should not rewrite `charge`.

Walkthrough: [effects showcase](../effects-showcase.md) ·
[effects basics](../tutorials/effects-basics.md).

The browser tutorial interpreter does not run real `effect` / `handle`. Keep
native examples under `./flow run`.

## Dynamics and time: describe evolution, then step

When the problem is a system through time, start with a `flow` / `evolves`
description (or `dsys` for linear plants). Add integrators, hybrid `when` /
`reaches`, and analysis after the math reads cleanly.

```bash
./flow run examples/evolution/pendulum_evolves.flow
./flow gfx examples/evolution/lorenz_gfx.flow
```

Guides: [evolution tutorial](../tutorials/evolution.md) ·
[dynamics tutorial](../tutorials/dynamics.md) ·
[dynamics DSL](dynamics-dsl.md).

Do not bury the ODE inside a graphics frame callback with magic constants.
Keep the model pure enough to run headlessly under `./flow record` and in
tests that check a known invariant.

## Autodiff and numerics

- Prefer stdlib dual / reverse helpers for small models; use checked-in grad
  codegen where the demos do today (`examples/ml/models/mlp_xor.flow`).
- Gate training demos on a measurable baseline so CI catches silent regressions.
- Keep loss and model separate from printing and file I/O (effects help).

## Memory and systems code

- Prefer arenas and clear ownership for hot paths ([memory](../library/memory.md)).
- Use `span<T>` / `span<mut T>` for borrowed views when the native compiler is
  in play ([spans](spans.md)).
- `@rt_safe` and RT docs exist for audio callbacks: no hidden allocation on the
  hot path ([rt-safety](../library/rt-safety.md), [rt-audio tutorial](../tutorials/rt-audio.md)).

Parser note: `ptr[0].field` is not supported; keep fields in locals or explicit
structs when targeting current codegen limits.

## Errors and control flow

- Prefer `Result`-shaped returns or early `return` over boolean out-params for
  new APIs ([errors tutorial](../tutorials/errors.md)).
- Use `match` for tagged choices when the native surface supports your case;
  integer tag matches are fine for teaching shapes in the browser.
- Fail loud in demos: non-zero exit when a gate fails (galleries and ML demos
  already do this).

## Graphics, audio, and demos

- One program, one job: a gallery clip should teach one idea.
- Record jobs with `./flow record` / `scripts/record_demos.py` so docs stay
  honest ([galleries](../demos/overview.md)).
- Keep simulation stepping separate from present/blit so the same model runs
  headless.

## Project hygiene

```bash
./flow test --strict --tier2
./flow fmt path/to/file.flow
```

- Match examples under `examples/` for style before inventing a new dialect.
- Document native-only features with the exact `./flow …` command; do not claim
  the browser runner executes gfx, effects, or `evolves`.
- Decision authority for language design stays with humans
  ([CONTRIBUTING](../../CONTRIBUTING.md)); implementation can move fast inside
  that envelope.

## Anti-patterns

| Smell | Prefer |
|---|---|
| God `main` that opens a window, steps physics, trains a net, and parses CLI | Split model / view / driver |
| Effects used as a global singleton with no handler swap | Handler per environment |
| Copy-pasted Euler in five files | One `flow` / shared step function |
| `ptr` + guessed length across API boundaries | `span` or sized arrays |
| Tutorial-only stand-ins shipped as production truth | Label stand-ins; link `./flow run` |

## A short recipe

1. Write the pure model (structs, `flow` / functions, pipelines).
2. Put I/O and time behind effects or a thin driver.
3. Add a gate: a number or invariant CI can check.
4. Only then attach gfx, audio, or WASM packaging.

That order is what "fluid abstract programming" means in Flow: stay in the
problem's language as long as possible, then compile down.
