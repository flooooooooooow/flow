# examples.verify.math.derived

*Union difference with empty preserves cardinality.*

**Source.** graham-knuth-patashnik — *Concrete Mathematics*

## Derived fact 1 — card((s ∪ t) \ empty) = card(s ∪ t)

**Coordinate.** Finset · cardinality · union diff empty card bound · **Derived fact**

*Source: graham-knuth-patashnik*

*Built on: union diff empty card derived, for cardinality on Finset*

> **Goal.** card((s ∪ t) \ empty) = card(s ∪ t)
>
> $$\forall s \in Finset \forall t \in Finset\quad card((s ∪ t) \ empty) = card(s ∪ t)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that union diff empty card bound for cardinality on Finset. |  |  |
| ② | We invoke the derived fact governing cardinality on Finset: union diff empty card derived, for cardinality on Finset (instantiated for s, t). |  |  |
| ③ | From step 2, this implies card((s ∪ t) \ empty) equals card(s ∪ t). Hence proven. | ③ | $card((s ∪ t) \ empty) = card(s ∪ t)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ③ | step 2 |

`Finset · cardinality · union diff empty card bound`
