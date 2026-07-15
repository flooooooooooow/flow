# examples.verify.math.derived

*Intersection with empty has cardinality zero.*

**Source.** graham-knuth-patashnik — *Concrete Mathematics*

## Derived fact 1 — card(s ∩ empty) = 0

**Coordinate.** Finset · cardinality · intersect empty has card zero · **Derived fact**

*Source: graham-knuth-patashnik*

*Built on: intersecting with empty gives empty, for cardinality on Finset, empty set has cardinality zero, for cardinality on Finset*

> **Goal.** card(s ∩ empty) = 0
>
> $$\forall s \in Finset\quad card(s ∩ empty) = 0$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that intersect empty has card zero for cardinality on Finset. |  |  |
| ② | We invoke the derived fact governing cardinality on Finset: intersecting with empty gives empty, for cardinality on Finset (instantiated for s). |  |  |
| ③ | We invoke the derived fact governing cardinality on Finset: empty set has cardinality zero, for cardinality on Finset. |  |  |
| ④ | From step 2 and step 3, this implies card(s ∩ empty) equals 0. Hence proven. | ④ | $card(s ∩ empty) = 0$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`Finset · cardinality · intersect empty has card zero`
