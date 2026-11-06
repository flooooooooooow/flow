# Idiomatic Flow: modernization guide

Flow examples should teach the highest-level **implemented and verified** expression of a computation, while retaining explicit lower-level versions when they explain performance, memory, ABI, or compiler behavior.

## Choose the abstraction that expresses the intent

| Intent | Prefer when supported | Keep explicit code for |
| --- | --- | --- |
| Transform a value through stages | `value |> transform |> summarize` | Evaluation-order and allocation demonstrations |
| Compute several views of one value | A named or inferred pipeline fork | Separate calls where sharing or typing differs |
| Select a transformation based on state | `|> choose selector { ... }` | Branching that changes side effects or control flow |
| Compute derivatives | Operators on `Dual` values | Derivative implementation and numerical comparisons |
| Express physical dynamics | Verified dynamics DSL examples | Integration algorithms, state mutation and solver internals |
| Work with concurrency | Verified channels and parallel constructs | Scheduling and synchronization internals |

The pipeline, fork and `choose` syntax are documented in [Flow Syntax](language/syntax.md). See the existing [natural physics example](../examples/physics/natural_syntax_demo.flow), [autodiff operators example](../examples/ml/autodiff/autodiff_clean_syntax.flow), and [dynamics example](../examples/dynamics/ga_dsys_syntax.flow) for concrete code.

## Rewrite policy

Start with an existing runnable example. Identify boilerplate that obscures the problem, then replace it only with constructs implemented on the target branch. Preserve input/output behavior, numerical tolerances, effects, ownership and execution order. Do not replace a working example with speculative syntax.

For each substantial rewrite, keep a before/after comparison in the PR description and run the repository's example verification as well as the specific example. A documentation example that does not compile must be explicitly labeled pseudocode, never presented as executable Flow.

Prefer concise, descriptive identifiers and direct expressions. Avoid introducing abstraction merely to reduce line count. Retain low-level examples under an advanced or implementation-focused heading when they teach an important mechanism.

## Modernization targets

Review [the language syntax reference](language/syntax.md), [the examples catalog](../examples/README.md), [autodiff](library/autodiff.md), and the existing physics, dynamics, numerical, ML, concurrency, audio and data examples. Promote verified idiomatic examples into the canonical entrypoints only after checking they work with the documented build.

When new language features land, update the language reference, a minimal executable fixture, a domain example, and the relevant tutorial together. Distinguish merged features from experimental or planned constructs.
