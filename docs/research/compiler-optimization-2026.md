# Compiler research: verified rewrite extraction (P0 experiment)

Tracking issue: [#1668](https://github.com/flooooooooooow/flow/issues/1668). Design context: [#1515](https://github.com/flooooooooooow/flow/issues/1515).

## What is implemented

`tools/compiler_research/contracts.flow` is an **experimental, self-contained, Flow-native local rewrite validator and deterministic candidate extractor**. It intentionally does not change production `flowc` lowering, C/MLIR backends, FIR-G's public interface, source syntax, or any optimizer flags.

The trusted input is a bounded expression DAG. A candidate supplies a source root, replacement root, rewrite rule, estimated cost, representation-preservation bits and estimated peak memory. The validator does not trust candidate cost or metadata as proof of correctness. Instead it checks one of three *exact syntax-matched* i32 rules: `x + 0 -> x`, `x * 1 -> x`, and `x + y -> y + x` when both expressions are pure. It checks child types, the literal value, matched structure, and transitively propagated effect bits before accepting. Invalid indices and cycles fail closed through an unknown-effect sentinel. Reassociation and all floating-point arithmetic rewrites are unsupported; signed-zero and NaN behavior would need a separate approved contract.

The extractor separately enforces representation properties, cost and peak memory ceilings. It uses a stable candidate-id tie-breaker and always retains the source representation as fallback. There is no mutable graph rewrite: the chosen output is an existing node id. This models a narrow **legality-before-profitability** boundary rather than a general equality-saturation engine. The `local-i32-rule` validation string in the demo is a scope label, *not* a certified formal theorem or proof of a whole program.

Run the deterministic JSON demo using:

```text
./flow tool compiler_research
```

Run the focused regression gate with:

```text
./flow test-lang tests/lang/test_compiler_research_contracts.flow
```

The gate covers valid identities, a deliberately invalid identity, effectful reordering, floating-point prohibition, invalid indices, preservation and memory restrictions, cost selection, stable tie-breaking and fallback. All source files are Flow. Since `compiler/src/` is untouched, there is no bootstrap C regeneration.

## Explicitly not implemented

This experiment is not a production optimizer and does not implement general e-graphs, Statewalk DP, learned extraction, semiring vectorization, hardware profiling, GPU proofs, PTX codegen, ISA-derived backend generation, timing guarantees, AI lowering, or Deegen-style VM generation. Those remain tracked in #1668 / existing related issues and need individually verified follow-ups. Input DAG metadata must come from an independently checked compiler representation before any production integration.

## Decision boundary for follow-up

Keep transformations legal under Flow's *existing* numerical and effect semantics. Any proposed source syntax, equivalence-model change, effect semantics, report schema commitment, or proof authority needs maintainers' explicit design decision, as required by `AGENTS.md` and `docs/project/agentic-loop.md`. The first integration candidate should use the existing FIR-G/denotational IR and `flowc_fact_can_optimize` status boundary rather than adding a rival semantic fact model. Subsequent PRs should demonstrate failures of the old implementation and carry end-to-end C/MLIR parity, runtime effect tests and reproducible performance evidence.
