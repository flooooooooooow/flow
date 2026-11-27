# Interaction-net execution: bounded Flow-native reference

**Status:** isolated experiment (2026-11-27), not a Flow 1.0 feature, not a
production FIR-G pass, not a parallel scheduler, and not a language proposal.

## Motivation

Frostbite's interaction-net execution model is interesting because local
principal-port interactions expose independent ready work without asking source
programs to explicitly schedule it. This repository already has the FIR-G
program-graph experiment ([FIR-G](../project/fir-g.md)) and a separate
verified-rewrite legality experiment
([contracts](compiler-optimization-2026.md)). Neither is a runtime interaction
net. This experiment establishes a small executable oracle before modifying
compiler lowering.

References:

- Yves Lafont, *Interaction Combinators*, Information and Computation 137(1),
  1997; especially Figure 2, which defines all six local rules and Figure 3,
  which demonstrates nontermination.
- Architect Labs, *Introducing Frostbite*, 2026-11-18:
  https://architectlabs.com/blog/frostbite

## Representation and invariants

`tools/interaction_nets/core.flow` implements a serial, bounded port graph.
Node kinds are gamma (constructor), delta (duplicator), epsilon (eraser), and
an inert boundary marker for observable free interfaces. Gamma and delta have
a principal port 0 and auxiliary ports 1 and 2; epsilon and boundary have
only port 0.

Nodes are stored in an externally allocated, fixed-capacity array. Port
`3 * node_id + port_number` holds a reciprocal link or `-1` for an
unattached interface. A validator checks kinds, live/dead states, port arity,
in-range peers, and reciprocal links. Every rewrite consumes its two agents
and preserves the observable outside wiring. Tombstoned nodes are not reused.

A *redex* is exactly two combinators wired principal-to-principal. Inert
boundary nodes cannot participate in an interaction. Every action is local
to a single active pair and the wires at its auxiliary interface; no source
expressions, control-flow blocks, or effect operations are interpreted.

The six implemented rules are:

| Active pair | Rewrite |
| --- | --- |
| gamma-gamma | annihilate and join opposite-numbered auxiliary ports |
| delta-delta | annihilate and join same-numbered auxiliary ports |
| epsilon-epsilon | annihilate both |
| gamma-epsilon | replace by two epsilon nodes at gamma's exposed auxiliaries |
| delta-epsilon | replace by two epsilon nodes at delta's exposed auxiliaries |
| gamma-delta | replace by four agents in a 2-by-2 commuting square |

Gamma and delta annihilation **must not be conflated**: Lafont's numbering
crosses gamma-gamma but not delta-delta. These rules are checked against the
original diagram, not presumed equivalent from their informal names.

## Defined limits

This implementation is a strict subset of valid interaction-net topologies.
A reducible pair must have each auxiliary port connected to a distinct,
external endpoint, not a dangling or internal-looping auxiliary. Such pairs
return `INET_INVALID` without mutation. Net validation itself permits
unattached ports, so construction can proceed incrementally.

Fixed capacity is checked before every rewrite. Insufficient capacity returns
`INET_CAPACITY` and keeps the graph unchanged. The run loop accepts a
step budget; reaching it with remaining active pairs returns `INET_LIMIT`.
A normal form has no remaining combinator/combinator active pair. This is
not a guarantee of termination.

The reducer is sequential. Per-step full-net validation is intentionally
slow, providing a conservative reference implementation. No effects,
allocation safety, arithmetic equivalence, compiler conversion, fibers,
thread safety, GPU lowering, proof certificate, or speedup claim is implied.
A pass-level integration must *not* assume FIR-G nodes are already linear,
fully owned, or safely duplicable.

## Run

```text
./flow test-lang tests/lang/test_interaction_nets.flow
./flow tool interaction_nets
```

The regression program checks each of the six rule classes (including
reversed orientation), reciprocal edges, malformed wiring, capacity
exhaustion without mutation, step-limit handling, and the order independence
of two disjoint redexes.

The runner constructs 256 independent gamma-gamma / delta-delta pairs. It
verifies the expected boundary permutations after serial reduction and
prints a one-line JSON measurement with allocations and elapsed milliseconds.
It is a **microbenchmark of the reference engine**, not a C/MLIR
equivalence or a parallel-speed benchmark.

## Path to FIR-G integration

The next step is a *separate* opt-in FIR-G-to-net conversion for a carefully
specified pure, alias-free subset. It must reject effectful/unknown ops,
pointer alias ambiguity, unsupported lifetime escapes, and unsupported
numerical rewrites before building a graph. Conversion needs observable
program-result tests rather than only graph wiring tests.

Only after a differential Flow C/MLIR oracle, normal-form graph-isomorphism
checks (not raw node-ID comparisons), bounded-resource tests, and
cycle/nontermination tests should concurrent reduction be investigated.
FIR-G remains the source of facts about effects and data dependencies;
`tools/compiler_research/contracts.flow` remains the initial
legality-before-profitability boundary. A concurrent engine would additionally
need contention-safe allocation, wire atomicity, ownership transfer, and
deterministic failure semantics.

For predictable-latency paths such as audio callbacks, conventional static
lowering should remain the default unless WCET and allocation bounds can be
established. A cost model must compare actual end-to-end execution including
graph construction and reduction costs, not just count independent redexes.

No source syntax, public effect contract, ownership law, or backend default
changes in this experiment.
