# examples.verify.math.derived

*Union intersect difference with empty is the intersection.*

**Source.** graham-knuth-patashnik — *Concrete Mathematics*

## Derived fact 1 — ((s ∪ t) ∩ s) \ empty = (s ∪ t) ∩ s

**Coordinate.** Finset · difference · union intersect diff empty derived · **Derived fact**

*Source: graham-knuth-patashnik*

*Built on: difference with empty preserves the set, for difference on Finset, union intersect self card derived, for cardinality on Finset*

> **Goal.** ((s ∪ t) ∩ s) \ empty = (s ∪ t) ∩ s
>
> $$\forall s \in Finset \forall t \in Finset\quad ((s ∪ t) ∩ s) \ empty = (s ∪ t) ∩ s$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that union intersect diff empty derived for difference on Finset. |  |  |
| ② | We invoke the derived fact governing difference on Finset: difference with empty preserves the set, for difference on Finset (instantiated for (s ∪ t) ∩ s). |  |  |
| ③ | We invoke the derived fact governing cardinality on Finset: union intersect self card derived, for cardinality on Finset (instantiated for s, t). |  |  |
| ④ | From step 2 and step 3, this implies ((s ∪ t) ∩ s) \ empty equals (s ∪ t) ∩ s. Hence proven. | ④ | $((s ∪ t) ∩ s) \ empty = (s ∪ t) ∩ s$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`Finset · difference · union intersect diff empty derived`
