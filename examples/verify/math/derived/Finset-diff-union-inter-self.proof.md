# examples.verify.math.derived

*Difference union intersection with self is empty.*

**Source.** graham-knuth-patashnik — *Concrete Mathematics*

## Derived fact 1 — (s \ t) ∪ (s ∩ t) \ (s \ t) = empty

**Coordinate.** Finset · difference · diff union intersect self derived · **Derived fact**

*Source: graham-knuth-patashnik*

*Built on: diff union inter self derived, for difference on Finset, diff union inter card bound, for cardinality on Finset*

> **Goal.** (s \ t) ∪ (s ∩ t) \ (s \ t) = empty
>
> $$\forall s \in Finset \forall t \in Finset\quad ((s \ t) ∪ (s ∩ t)) \ (s \ t) = empty$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that diff union intersect self derived for difference on Finset. |  |  |
| ② | We invoke the derived fact governing difference on Finset: diff union inter self derived, for difference on Finset (instantiated for s, t). |  |  |
| ③ | We invoke the derived fact governing cardinality on Finset: diff union inter card bound, for cardinality on Finset (instantiated for s, t). |  |  |
| ④ | From step 2 and step 3, this implies ((s \ t) ∪ (s ∩ t)) \ (s \ t) equals empty. Hence proven. | ④ | $((s \ t) ∪ (s ∩ t)) \ (s \ t) = empty$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`Finset · difference · diff union intersect self derived`
