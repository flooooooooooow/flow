# examples.verify.math.derived

*Cardinality is monotone under union on the left.*

**Source.** graham-knuth-patashnik — *Concrete Mathematics*

## Derived fact 1 — card(a) <= card(a ∪ b)

**Coordinate.** Finset · cardinality · size is monotone under union on the left · **Derived fact**

*Source: graham-knuth-patashnik*

*Built on: union size is at most the sum, for cardinality on Finset, less-or-equal is reflexive, for order on the natural numbers*

> **Goal.** card(a) <= card(a ∪ b)
>
> $$\forall a \in Finset \forall b \in Finset\quad card(a) \le card(a ∪ b)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that size is monotone under union on the left for cardinality on Finset. |  |  |
| ② | We invoke the derived fact governing cardinality on Finset: union size is at most the sum, for cardinality on Finset (instantiated for a, b). |  |  |
| ③ | We invoke the derived fact governing order on the natural numbers: less-or-equal is reflexive, for order on the natural numbers (instantiated for card(a)). |  |  |
| ④ | From step 2 and step 3, this implies card(a) is at most card(a ∪ b). Hence proven. | ④ | $card(a) \le card(a ∪ b)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`Finset · cardinality · size is monotone under union on the left`
