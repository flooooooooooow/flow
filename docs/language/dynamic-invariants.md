# Dynamic invariant discovery

Flow includes a Flow-native dynamic invariant discovery core in
`compiler/src/dynamic_invariants.flow`.

The purpose is profile-guided discovery, not proof. Runtime observations can
suggest useful specialisations, but an observed property is never silently
promoted to a compiler fact.

## Model

For an observed scalar value, the miner maintains a compact online summary:

```text
samples
first / last
observed min / max
zero / positive / negative counts
gcd(value - first)
gcd(abs(value))
number of value changes
```

From that state it can propose candidates such as:

```text
x == constant
lo <= x <= hi
x != 0
x >= 0
x > 0
x == first (mod m)
x is aligned to 2^k
```

For a pair of observed values it tracks:

```text
x == y
x != y
x <  y
x <= y
x >  y
x >= y
```

All discovery is online, deterministic and allocation-free after the state
object itself exists. The implementation is written in Flow.

## Optimisation safety

The public policy function
`flowc_dyn_optimization_mode(candidate_holds, statically_proven, guard_available)`
has only three outcomes:

```text
FLOWC_DYN_USE_NONE
FLOWC_DYN_USE_GUARDED
FLOWC_DYN_USE_PROVEN
```

A candidate is therefore usable only when either:

1. static analysis independently proves the property, or
2. code generation inserts a runtime guard and retains a generic fallback.

This deliberately separates empirical discovery from semantic truth.

A future instrumentation pass can therefore perform:

```text
Flow source
    |
    v
instrument candidate values
    |
    v
representative executions
    |
    v
FlowcDynScalar / FlowcDynPair
    |
    v
candidate invariants
    |
    +--> static proof --> unconditional optimisation
    |
    +--> runtime guard --> specialised path + generic fallback
    |
    +--> neither -------> no optimisation
```

## Example

```flow
import "compiler/src/dynamic_invariants.flow"

function profile_stride() -> i32 {
    let mut stride: FlowcDynScalar = flowc_dyn_scalar_new(1)

    flowc_dyn_scalar_observe(&stride, 16)
    flowc_dyn_scalar_observe(&stride, 20)
    flowc_dyn_scalar_observe(&stride, 24)
    flowc_dyn_scalar_observe(&stride, 28)

    # Observed values are 4-congruent and all divisible by 4.
    if flowc_dyn_scalar_congruence_mod(stride, 4) != 4 {
        return 1
    }
    if flowc_dyn_scalar_alignment(stride, 4) != 4 {
        return 2
    }

    return 0
}
```

The second argument to candidate queries is the minimum number of observations
required before the candidate may be surfaced.

## Scope

The first implementation intentionally mines integer relations that are cheap
and directly actionable by range analysis, vectorisation, alignment
specialisation and guarded code generation.

Floating-point tolerance relations, array shape/stride observations, affine
relations, instrumentation insertion, persisted profile files and automatic
specialisation are separate layers. They should build on this core rather than
weakening the rule that observed invariants are hypotheses.

The executable regression test is
`tests/lang/test_dynamic_invariants.flow`.


## Integration with the semantic stack

Dynamic candidates now materialise as the shared `FlowcSemanticFact` type.
`flowc_dyn_scalar_facts` and `flowc_dyn_pair_facts` emit observed facts
with dynamic provenance and a caller-supplied recognition-domain mask.

The recognition/residual pipeline is documented in
[Semantic stack](semantic-stack.md). Runtime discovery remains an evidence
source; it does not acquire proof authority merely because a pattern is stable.
