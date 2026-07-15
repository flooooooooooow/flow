# examples.verify.math.derived

*Union intersect difference with self is empty.*

**Source.** graham-knuth-patashnik — *Concrete Mathematics*

## Derived fact 1 — ((s ∪ t) ∩ s) \ ((s ∪ t) ∩ s) = empty

**Coordinate.** Finset · difference · union intersect diff self derived · **Derived fact**

*Source: graham-knuth-patashnik*

*Built on: intersection diff self is empty, for difference on Finset, union intersect self card derived, for cardinality on Finset*

> **Goal.** ((s ∪ t) ∩ s) \ ((s ∪ t) ∩ s) = empty
>
> $$\forall s \in Finset \forall t \in Finset\quad ((s ∪ t) ∩ s) \ ((s ∪ t) ∩ s) = empty$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that union intersect diff self derived for difference on Finset. |  |  |
| ② | We invoke the derived fact governing difference on Finset: intersection diff self is empty, for difference on Finset (instantiated for s, t). |  |  |
| ③ | We invoke the derived fact governing cardinality on Finset: union intersect self card derived, for cardinality on Finset (instantiated for s, t). |  |  |
| ④ | From step 2 and step 3, this implies ((s ∪ t) ∩ s) \ ((s ∪ t) ∩ s) equals empty. Hence proven. | ④ | $((s ∪ t) ∩ s) \ ((s ∪ t) ∩ s) = empty$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`Finset · difference · union intersect diff self derived`
