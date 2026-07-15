# examples.verify.math.derived

*Empty on the left in intersection has cardinality zero.*

**Source.** graham-knuth-patashnik — *Concrete Mathematics*

## Derived fact 1 — card(empty ∩ s) = 0

**Coordinate.** Finset · cardinality · empty left intersection has size zero · **Derived fact**

*Source: graham-knuth-patashnik*

*Built on: empty on the left gives empty, for intersection on Finset, the empty set has size zero, for cardinality on Finset*

> **Goal.** card(empty ∩ s) = 0
>
> $$\forall s \in Finset\quad card(empty ∩ s) = 0$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that empty left intersection has size zero for cardinality on Finset. |  |  |
| ② | We invoke the derived fact governing intersection on Finset: empty on the left gives empty, for intersection on Finset (instantiated for s). |  |  |
| ③ | We invoke the definitional clause governing cardinality on Finset: the empty set has size zero, for cardinality on Finset. |  |  |
| ④ | From step 2 and step 3, this implies card(empty ∩ s) equals 0. Hence proven. | ④ | $card(empty ∩ s) = 0$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`Finset · cardinality · empty left intersection has size zero`
