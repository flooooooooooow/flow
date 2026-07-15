# examples.verify.math.derived

*Finite set union associates.*

**Source.** graham-knuth-patashnik

## Derived fact 1 — (a ∪ b) ∪ c = a ∪ (b ∪ c)

**Coordinate.** Finset · union · parentheses do not matter · **Derived fact**

*Source: graham-knuth-patashnik*

*Built on: order does not matter, for union on Finset, empty is the left identity, for union on Finset*

> **Goal.** (a ∪ b) ∪ c = a ∪ (b ∪ c)
>
> $$\forall a \in Finset \forall b \in Finset \forall c \in Finset\quad (a ∪ b) ∪ c = a ∪ (b ∪ c)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that parentheses do not matter for union on Finset. |  |  |
| ② | We invoke the derived fact governing union on Finset: order does not matter, for union on Finset (instantiated for a, b). |  |  |
| ③ | We invoke the derived fact governing union on Finset: order does not matter, for union on Finset (instantiated for b, c). |  |  |
| ④ | We invoke the definitional clause governing union on Finset: empty is the left identity, for union on Finset (instantiated for a). |  |  |
| ⑤ | From step 2, step 3, and step 4, this implies (a ∪ b) ∪ c equals a ∪ (b ∪ c). Hence proven. | ⑤ | $(a ∪ b) ∪ c = a ∪ (b ∪ c)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ⑤ | step 2, step 3, and step 4 |

`Finset · union · parentheses do not matter`
