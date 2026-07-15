# examples.verify.math.derived

*Cardinality of union intersected with self is bounded.*

**Source.** graham-knuth-patashnik — *Concrete Mathematics*

## Derived fact 1 — card((s ∪ t) ∩ s) <= card(s ∪ t)

**Coordinate.** Finset · cardinality · union intersect self card bound · **Derived fact**

*Source: graham-knuth-patashnik*

*Built on: intersection card is at most left card, for cardinality on Finset*

> **Goal.** card((s ∪ t) ∩ s) <= card(s ∪ t)
>
> $$\forall s \in Finset \forall t \in Finset\quad card((s ∪ t) ∩ s) \le card(s ∪ t)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that union intersect self card bound for cardinality on Finset. |  |  |
| ② | We invoke the derived fact governing cardinality on Finset: intersection card is at most left card, for cardinality on Finset (instantiated for s ∪ t, s). |  |  |
| ③ | From step 2, this implies card((s ∪ t) ∩ s) is at most card(s ∪ t). Hence proven. | ③ | $card((s ∪ t) ∩ s) \le card(s ∪ t)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ③ | step 2 |

`Finset · cardinality · union intersect self card bound`
