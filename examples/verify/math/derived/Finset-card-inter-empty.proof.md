# examples.verify.math.derived

*Intersecting with the empty set has cardinality zero.*

**Source.** graham-knuth-patashnik — *Concrete Mathematics*

## Derived fact 1 — card(s ∩ empty) = 0

**Coordinate.** Finset · cardinality · intersection with empty has size zero · **Derived fact**

*Source: graham-knuth-patashnik*

*Built on: empty on the right gives empty, for intersection on Finset, the empty set has size zero, for cardinality on Finset*

> **Goal.** card(s ∩ empty) = 0
>
> $$\forall s \in Finset\quad card(s ∩ empty) = 0$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that intersection with empty has size zero for cardinality on Finset. |  |  |
| ② | We invoke the derived fact governing intersection on Finset: empty on the right gives empty, for intersection on Finset (instantiated for s). |  |  |
| ③ | We invoke the definitional clause governing cardinality on Finset: the empty set has size zero, for cardinality on Finset. |  |  |
| ④ | From step 2 and step 3, this implies card(s ∩ empty) equals 0. Hence proven. | ④ | $card(s ∩ empty) = 0$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`Finset · cardinality · intersection with empty has size zero`
