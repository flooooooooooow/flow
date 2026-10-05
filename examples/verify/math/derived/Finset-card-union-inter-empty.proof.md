# examples.verify.math.derived

*Union intersected with empty has cardinality zero.*

**Source.** graham-knuth-patashnik — *Concrete Mathematics*

## Derived fact 1 — card((a ∪ b) ∩ empty) = 0

**Coordinate.** Finset · cardinality · union intersect empty has size zero · **Derived fact**

*Source: graham-knuth-patashnik*

*Built on: union with empty on the right annihilates, for intersection on Finset, the empty set has size zero, for cardinality on Finset*

> **Goal.** card((a ∪ b) ∩ empty) = 0
>
> $$\forall a \in Finset \forall b \in Finset\quad card((a ∪ b) ∩ empty) = 0$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that union intersect empty has size zero for cardinality on Finset. |  |  |
| ② | We invoke the derived fact governing intersection on Finset: union with empty on the right annihilates, for intersection on Finset (instantiated for a, b). |  |  |
| ③ | We invoke the definitional clause governing cardinality on Finset: the empty set has size zero, for cardinality on Finset. |  |  |
| ④ | From step 2 and step 3, this implies card((a ∪ b) ∩ empty) equals 0. Hence proven. | ④ | $card((a ∪ b) ∩ empty) = 0$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`Finset · cardinality · union intersect empty has size zero`
