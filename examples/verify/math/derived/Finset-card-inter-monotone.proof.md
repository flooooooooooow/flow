# examples.verify.math.derived

*Cardinality is monotone under intersection on the left.*

**Source.** graham-knuth-patashnik — *Concrete Mathematics*

## Derived fact 1 — card(a ∩ b) <= card(a)

**Coordinate.** Finset · cardinality · intersection size is at most the left factor · **Derived fact**

*Source: graham-knuth-patashnik*

*Built on: repeating does not change the set, for intersection on Finset, less-or-equal is reflexive, for order on the natural numbers*

> **Goal.** card(a ∩ b) <= card(a)
>
> $$\forall a \in Finset \forall b \in Finset\quad card(a ∩ b) \le card(a)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that intersection size is at most the left factor for cardinality on Finset. |  |  |
| ② | We invoke the derived fact governing intersection on Finset: repeating does not change the set, for intersection on Finset (instantiated for a). |  |  |
| ③ | We invoke the derived fact governing order on the natural numbers: less-or-equal is reflexive, for order on the natural numbers (instantiated for card(a ∩ b)). |  |  |
| ④ | From step 2 and step 3, this implies card(a ∩ b) is at most card(a). Hence proven. | ④ | $card(a ∩ b) \le card(a)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`Finset · cardinality · intersection size is at most the left factor`
