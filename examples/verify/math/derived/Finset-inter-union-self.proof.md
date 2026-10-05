# examples.verify.math.derived

*Intersection distributes over self-union.*

**Source.** graham-knuth-patashnik — *Concrete Mathematics*

## Derived fact 1 — s ∩ (s ∪ s) = s

**Coordinate.** Finset · intersection · intersect with self union · **Derived fact**

*Source: graham-knuth-patashnik*

*Built on: intersecting with self union gives self, for intersection on Finset*

> **Goal.** s ∩ (s ∪ s) = s
>
> $$\forall s \in Finset\quad s ∩ (s ∪ s) = s$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that intersect with self union for intersection on Finset. |  |  |
| ② | We invoke the derived fact governing intersection on Finset: intersecting with self union gives self, for intersection on Finset (instantiated for s). |  |  |
| ③ | From step 2, this implies s ∩ (s ∪ s) equals s. Hence proven. | ③ | $s ∩ (s ∪ s) = s$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ③ | step 2 |

`Finset · intersection · intersect with self union`
