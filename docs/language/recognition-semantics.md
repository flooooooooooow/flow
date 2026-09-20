# Recognition-relative semantics

Flow treats a program as a mathematical system before it treats that program as
a particular control-flow graph, SSA graph, C translation unit, or machine
program. Recognition-relative semantics makes that separation explicit.

For a flow (P), let (D(P)) be its latent denotation. A recognition domain
(q) is a projection (G_q) of that denotation:

[
    [[P]]_q = G_q(D(P))
]

Two programs can therefore be equivalent for one observer and different for
another:

[
    [[P]]_a = [[Q]]_a
    quad	ext{while}quad
    [[P]]_b \ne [[Q]]_b
]

This is useful for compiler transformations. A rewrite is valid for a flow's
declared recognition contract when every protected projection is preserved.

## Syntax

```flow
flow Controller {
    state x : f64 = 0.0
    input u : f64
    output y : f64 = x
    param k : f64 = 2.0

    solver { dt 1 ms method euler }
    x evolves as k * u

    always {
        x < 100.0
    }

    recognize {
        numerical
        realtime
        causal
        safety
        memory
    }
}
```

`recognize` is contextual. It remains a legal identifier outside
`recognize { ... }` in a flow body. Domains may be separated by whitespace or
commas.

The currently defined domains are:

| Domain | Projection currently includes |
|---|---|
| `numerical` | schemas, initial/default values, continuous dynamics, output maps, solver/timing, events, discrete updates |
| `realtime` | schemas, solver/timing, events, discrete updates, composition |
| `causal` | state/input/output schemas, dynamics, output maps, events, discrete updates, composition |
| `safety` | schemas, dynamics, events, discrete updates, `always`/`never` constraints |
| `memory` | member schemas, hidden event/timer state shape, child-flow composition |

These projections are deliberately not aliases for compiler backends. They
describe which distinctions are observable to a semantic regime.

## Compiler API

`src/flow/recognition.py` exposes:

```python
denotation(flow)
recognition_signature(flow, domain)
recognition_manifest(flow)
compare_recognition(before, after, domains)
assert_recognition_preserved(before, after, domains)
```

Parsing records the contract on `FlowDecl.recognition`. Flow lowering keeps
the original declaration on `StructDecl.flow_decl` and adds a canonical
`StructDecl.recognition_manifest`. Later optimization and IR passes can use
the comparison API before accepting a rewrite.

For example, changing a derivative changes the `numerical` projection but
does not change the `memory` projection when the state layout is unchanged.
That is intentional: recognition equivalence is observer-relative rather than
a single global equality relation.

## What this does not claim yet

This first implementation provides semantic contracts and deterministic
projections. It does not yet prove backend machine code satisfies those
contracts, calculate WCET, model floating-point error bounds, or attach
tolerances to approximate equivalence. Those can be layered on the same API
without changing the surface syntax.

The intended compiler relation is:

[
    P \equiv_q Q
    iff
    G_q(D(P)) = G_q(D(Q))
]

and for a flow protecting a set of domains (Q_P):

[
    P \equiv_{Q_P} Q
    iff
    \forall q \in Q_P,; P \equiv_q Q
]

This makes "lowering preserves meaning" precise without requiring one
representation to be treated as the whole meaning of the program.
