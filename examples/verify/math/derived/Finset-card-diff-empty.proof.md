# examples.verify.math.derived

*Difference with empty leaves cardinality unchanged.*

**Source.** graham-knuth-patashnik — *Concrete Mathematics*

## Derived fact 1 — card(s \ empty) = card(s)

**Coordinate.** Finset · cardinality · difference with empty preserves cardinality · **Derived fact**

*Source: graham-knuth-patashnik*

*Built on: difference with empty preserves cardinality, for cardinality on Finset*

> **Goal.** card(s \ empty) = card(s)
>
> $$\forall s \in Finset\quad card(s \ empty) = card(s)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that difference with empty preserves cardinality for cardinality on Finset. |  |  |
| ② | We cross the inductive boundary: assume the claim holds for s (the induction hypothesis). | ② | $card(s \ empty) = card(s)$ |
| ③ | From step 2, this implies card(s \ empty) equals card(s). Hence proven. | ③ | $card(s \ empty) = card(s)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ③ | step 2 |

`Finset · cardinality · difference with empty preserves cardinality`
