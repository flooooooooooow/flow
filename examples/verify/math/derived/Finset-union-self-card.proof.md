# examples.verify.math.derived

*Self-union preserves cardinality.*

**Source.** graham-knuth-patashnik — *Concrete Mathematics*

## Derived fact 1 — card(s ∪ s) = card(s)

**Coordinate.** Finset · cardinality · union with self preserves cardinality · **Derived fact**

*Source: graham-knuth-patashnik*

*Built on: union with self preserves cardinality, for cardinality on Finset*

> **Goal.** card(s ∪ s) = card(s)
>
> $$\forall s \in Finset\quad card(s ∪ s) = card(s)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that union with self preserves cardinality for cardinality on Finset. |  |  |
| ② | We cross the inductive boundary: assume the claim holds for s (the induction hypothesis). | ② | $card(s ∪ s) = card(s)$ |
| ③ | From step 2, this implies card(s ∪ s) equals card(s). Hence proven. | ③ | $card(s ∪ s) = card(s)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ③ | step 2 |

`Finset · cardinality · union with self preserves cardinality`
