# examples.verify.math.derived

*Self-intersection then empty has cardinality zero.*

**Source.** graham-knuth-patashnik — *Concrete Mathematics*

## Derived fact 1 — card((s ∩ s) ∩ empty) = 0

**Coordinate.** Finset · cardinality · self intersect empty card zero · **Derived fact**

*Source: graham-knuth-patashnik*

*Built on: self intersect empty derived, for intersection on Finset, empty set has cardinality zero, for cardinality on Finset*

> **Goal.** card((s ∩ s) ∩ empty) = 0
>
> $$\forall s \in Finset\quad card((s ∩ s) ∩ empty) = 0$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that self intersect empty card zero for cardinality on Finset. |  |  |
| ② | We invoke the derived fact governing intersection on Finset: self intersect empty derived, for intersection on Finset (instantiated for s). |  |  |
| ③ | We invoke the derived fact governing cardinality on Finset: empty set has cardinality zero, for cardinality on Finset. |  |  |
| ④ | From step 2 and step 3, this implies card((s ∩ s) ∩ empty) equals 0. Hence proven. | ④ | $card((s ∩ s) ∩ empty) = 0$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`Finset · cardinality · self intersect empty card zero`
