# FLOW Tutorials

Step-by-step learning paths with **browser compile & run** on every complete example.

- **[Interactive app](index.html)** — lesson picker with live editor (frontend, separate from native compiler)
- **Written guides** — beginner / intermediate / advanced (embedded runners on each `main` program)

For reference, see [LANGUAGE_SPEC.md](../LANGUAGE_SPEC.md).

## Learning Paths

### Path 1: Complete Beginner
1. [beginner.md](beginner.md) — Variables, functions, basic types
2. Run examples in `docs/examples/basic/`
3. Build: Calculator, Guessing game

### Path 2: Coming from Other Languages
1. Skim [LANGUAGE_SPEC.md](../LANGUAGE_SPEC.md) §1-5
2. [intermediate.md](intermediate.md) — Structs, modules, patterns
3. Run examples in `docs/examples/algorithms/`

### Path 3: Effect System Focus
1. Read [LANGUAGE_SPEC.md](../LANGUAGE_SPEC.md) §6
2. [advanced.md](advanced.md) — Effects deep-dive
3. Run `examples/effects_working.flow`

### Path 4: Dynamics & Control (the vision path)
1. [dynamics.md](dynamics.md) — ODE integrators → `dsys` → `sense` → `ga evolve`
2. Run the flagship suite in `examples/evolution/`
3. Read [VISION.md](../../VISION.md) and the [north-star grammar plan](../vision/north-star.md)

## Tutorial Files

| File | Duration | Prerequisites |
|------|----------|---------------|
| [beginner.md](beginner.md) | 30 min | None |
| [intermediate.md](intermediate.md) | 45 min | beginner.md |
| [advanced.md](advanced.md) | 60 min | intermediate.md |
| [dynamics.md](dynamics.md) | 60 min | intermediate.md |

## Exercises

Each tutorial includes exercises. Solutions are in `examples/`.
