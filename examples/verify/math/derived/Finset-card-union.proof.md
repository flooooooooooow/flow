# examples.verify.math.derived

*Cardinality of a union is bounded by the sum of cardinalities.*

**Source.** graham-knuth-patashnik

## Derived fact 1 — card(a ∪ b) ≤ card(a) + card(b)

**Coordinate.** Finset · cardinality · union size is at most the sum · **Derived fact**

*Source: graham-knuth-patashnik*

*Built on: the empty set has size zero, for cardinality on Finset, less-or-equal is reflexive, for order on the natural numbers*

> **Goal.** card(a ∪ b) ≤ card(a) + card(b)
>
> $$\forall a \in Finset \forall b \in Finset\quad card(a ∪ b) \le card(a) + card(b)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that union size is at most the sum for cardinality on Finset. |  |  |
| ② | We invoke the definitional clause governing cardinality on Finset: the empty set has size zero, for cardinality on Finset. |  |  |
| ③ | We invoke the derived fact governing order on the natural numbers: less-or-equal is reflexive, for order on the natural numbers (instantiated for card(a)). |  |  |
| ④ | From step 2 and step 3, this implies card(a ∪ b) is at most card(a) plus card(b). Hence proven. | ④ | $card(a ∪ b) \le card(a) + card(b)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`Finset · cardinality · union size is at most the sum`
