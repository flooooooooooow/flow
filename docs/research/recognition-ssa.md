# Recognition SSA (RSSA)

RSSA combines Flow recognition-relative semantics with typed/effectful SSA refinement. It does not replace SSA: the ordinary discrete refinement judgement remains mandatory and is extended by observer-relative dynamical obligations.

For a transformation P -> P', legality is P <=_(Q,epsilon) P' iff the ordinary SSA/effect refinement holds and, for every protected recognition domain q, d_q(R_q(P), R_q(P')) <= epsilon_q.

The first executable certificate model is in `src/flow/recognition_ssa.py`. `AttractorSignature` records finite representatives for fixed points, basin topology, stability and invariants. Basin-label changes are currently treated as hard violations; continuous components use bounded distances. This is intentionally conservative.

## Architecture

Flow source -> typed/effectful frontend -> RSSA obligations -> existing SSA/MLIR -> Stable C/LLVM.

Existing `recognize { ... }` declarations remain the source-level selection of protected observation domains. The current exact recognition checker remains valid. RSSA adds bounded dynamical refinement rather than changing that existing contract.

The implementation boundary is intentionally adapter-based: FIR-G, MLIR and future self-hosted IRs provide (1) their ordinary discrete refinement judgement and (2) observation functions producing attractor signatures. No backend becomes the semantic authority.

## Research programme

Phase R0 (landed on the research branch): executable recognition-indexed refinement certificates; exact conservative-extension behavior with no continuous contracts; tests for tolerance, basin preservation and mandatory discrete refinement.

Phase R1: define an RSSA adapter over the canonical Flow IR. Preserve conventional SSA joins/block arguments and attach recognition joins as metadata rather than changing phi semantics. Lower source recognition declarations to `RecognitionContract`s.

Phase R2: wrap optimization passes. Every participating pass emits a discrete refinement witness plus before/after recognition observations. Start with constant folding, DCE and reassociation; keep unsupported passes outside RSSA rather than pretending they are verified.

Phase R3: continuous semantics. Derive fixed-point, local stability and invariant witnesses for the tractable subset of `flow` dynamics. Add numerical certificates for approximate domains and exact certificates where symbolic reasoning is available.

Phase R4: effects/refinement integration. Recognition obligations become substructural transformation capabilities: passes may consume only explicitly granted approximation budgets. Effectful SSA refinement and recognition preservation remain separate premises of one legality judgement.

Phase R5: MLIR integration. Carry RSSA contracts as Flow-owned metadata through lowering, validate before destructive optimization boundaries, and emit certificate artifacts alongside optimized IR.

Phase R6: mechanization. Formalize a restricted calculus in Lean. Primary theorem: with Q empty (or only ordinary exact observables) and epsilon=0, RSSA reduces to ordinary SSA refinement. Secondary theorem: composition is budget-safe, so sequential transformations cannot silently exceed declared recognition drift.

## Non-goals

RSSA does not claim that arbitrary nonlinear dynamical equivalence is decidable. It does not redefine phi nodes as attractors. It does not replace compiler correctness with numerical similarity. Continuous recognition obligations strengthen or explicitly relax a conventional discrete refinement judgement; they never silently bypass it.
