# examples.verify.math.derived

*Cardinality of an intersection is at most the right operand.*

**Source.** graham-knuth-patashnik — *Concrete Mathematics*

## Derived fact 1 — card(a ∩ b) ≤ card(b)

**Coordinate.** Finset · cardinality · intersection size is at most the right factor · **Derived fact**

*Source: graham-knuth-patashnik*

*Built on: order does not matter, for intersection on Finset, intersection size is at most each factor, for cardinality on Finset*

> **Goal.** card(a ∩ b) ≤ card(b)
>
> $$\forall a \in Finset \forall b \in Finset\quad card(a ∩ b) \le card(b)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that intersection size is at most the right factor for cardinality on Finset. |  |  |
| ② | We invoke the derived fact governing intersection on Finset: order does not matter, for intersection on Finset (instantiated for a, b). |  |  |
| ③ | We invoke the derived fact governing cardinality on Finset: intersection size is at most each factor, for cardinality on Finset (instantiated for b, a). |  |  |
| ④ | From step 2 and step 3, this implies card(a ∩ b) is at most card(b). Hence proven. | ④ | $card(a ∩ b) \le card(b)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`Finset · cardinality · intersection size is at most the right factor`
