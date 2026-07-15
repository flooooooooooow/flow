# examples.verify.math.derived

*Self-union cardinality equals self cardinality.*

**Source.** graham-knuth-patashnik — *Concrete Mathematics*

## Derived fact 1 — card(s ∪ s) = card(s)

**Coordinate.** Finset · cardinality · union with self card derived · **Derived fact**

*Source: graham-knuth-patashnik*

*Built on: union with self preserves cardinality, for cardinality on Finset*

> **Goal.** card(s ∪ s) = card(s)
>
> $$\forall s \in Finset\quad card(s ∪ s) = card(s)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that union with self card derived for cardinality on Finset. |  |  |
| ② | We invoke the derived fact governing cardinality on Finset: union with self preserves cardinality, for cardinality on Finset (instantiated for s). |  |  |
| ③ | From step 2, this implies card(s ∪ s) equals card(s). Hence proven. | ③ | $card(s ∪ s) = card(s)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ③ | step 2 |

`Finset · cardinality · union with self card derived`
