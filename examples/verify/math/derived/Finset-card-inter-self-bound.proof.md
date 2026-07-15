# examples.verify.math.derived

*Self-intersection cardinality is at most self cardinality.*

**Source.** graham-knuth-patashnik — *Concrete Mathematics*

## Derived fact 1 — card(s ∩ s) <= card(s)

**Coordinate.** Finset · cardinality · self intersection card bound derived · **Derived fact**

*Source: graham-knuth-patashnik*

*Built on: intersection card is at most left card, for cardinality on Finset*

> **Goal.** card(s ∩ s) <= card(s)
>
> $$\forall s \in Finset\quad card(s ∩ s) \le card(s)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that self intersection card bound derived for cardinality on Finset. |  |  |
| ② | We invoke the derived fact governing cardinality on Finset: intersection card is at most left card, for cardinality on Finset (instantiated for s, s). |  |  |
| ③ | From step 2, this implies card(s ∩ s) is at most card(s). Hence proven. | ③ | $card(s ∩ s) \le card(s)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ③ | step 2 |

`Finset · cardinality · self intersection card bound derived`
