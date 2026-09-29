# Semantic stack

Flow's compiler semantics are organised as one evidence pipeline:

```text
static semantics
       +
denotational semantics
       +
dynamic invariant discovery
       +
recognition / residual analysis
       |
       v
proof or runtime guard
       |
       v
optimisation / lowering
```

The layers share `FlowcSemanticFact` from
`compiler/src/semantic_facts.flow`. This is the important boundary: the
compiler does not flatten static proof, language contracts and runtime
observations into one undifferentiated confidence score.

## Shared fact model

A semantic fact carries:

- relation kind and value ids;
- relation payload such as range, modulus or alignment;
- provenance: static, denotational, dynamic or learned;
- epistemic status: observed, contract, proven or guarded;
- recognition-domain visibility;
- runtime support and confidence metadata.

`flowc_fact_can_optimize` admits only `PROVEN` and `GUARDED` facts.
Observed structure cannot authorize an unconditional rewrite.

## Static semantics

`compiler/src/typecheck.flow` remains the authority for Stage-A static
well-typedness. `compiler/src/static_semantics.flow` is the bridge from
successful static analyses into the shared fact representation.

For example, a statically established range becomes a `PROVEN` range fact.
The module also contains a concrete AST collector for integer literals so this
bridge is executable rather than only an interface convention.

## Denotational semantics

`compiler/src/denotation.flow` gives the self-hosted compiler a Flow-native
structural denotation for a parsed `flow` declaration. It separates the same
semantic components used by the older host model:

```text
state/input/output/param schemas
initial state and parameter defaults
continuous dynamics
output maps
timing
events and discrete updates
constraints
composition
```

The self-hosted representation uses canonical lexer-token fingerprints for
components, so whitespace and comments do not affect them. These fingerprints
are semantic audit metadata, not proof objects.

## Recognition

`compiler/src/recognition.flow` reads the domains declared by:

```flow
recognize {
    numerical
    realtime
    causal
    safety
    memory
}
```

and projects a `FlowcDenotation` through those domains. A transformation can
therefore be checked for observer-relative semantic drift. For example,
changing a safety constraint changes the `safety` projection but not the
`numerical` projection.

Semantic facts use the same domain mask, so runtime or static information can
be visible to one recognition regime without being treated as globally
represented.

## Dynamic invariant discovery

`compiler/src/dynamic_invariants.flow` performs online invariant discovery
and now materialises candidates directly as `FlowcSemanticFact` values.

The scalar miner can emit range, constant, sign, nonzero, congruence and
power-of-two alignment observations. The pair miner emits equality and
ordering relations.

All of these facts have dynamic provenance and `OBSERVED` status.

## Residual layer

`compiler/src/residual.flow` defines a residual operationally:

> an observed semantic fact visible in the active recognition domain that is
> absent from the recogniser's represented fact set.

This makes the residual representation-relative rather than synonymous with
regression error.

A `FlowcResidualState` tracks whether the same residual survives independent
observation windows and whether it retains predictive utility. That produces a
structured-residual *candidate*. Persistence or predictivity still cannot turn
it into a compiler truth.

## Orchestration

`compiler/src/semantic_pipeline.flow` supplies an allocation-free semantic
ledger and the common projection/residual operations.

Conceptually:

```text
static analysis --------------------+
                                     |
denotation / contracts -------------+--> semantic fact ledger
                                     |          |
runtime invariant discovery --------+          v
                                         recognition projection
                                                |
                                                v
                                        represented / residual
                                                |
                                   +------------+------------+
                                   |                         |
                              static proof              runtime guard
                                   |                         |
                                   +------------+------------+
                                                |
                                                v
                                      optimisation/lowering
```

## Worked example

Suppose execution repeatedly produces:

```text
x = 16, 20, 24, 28
```

and the current recogniser already represents:

```text
16 <= x <= 28
x > 0
x != 0
alignment(x) = 4
```

Dynamic discovery also observes:

```text
x == 16 (mod 4)
```

The range/sign/alignment observations are already represented. The congruence
relation is therefore the residual.

If it persists across independent windows and predicts held-out executions, it
becomes a structured-residual candidate. The compiler may still exploit it
only if static analysis proves it or code generation emits an executable guard
with a generic fallback.

The executable end-to-end regression is
`tests/lang/test_semantic_stack.flow`.
