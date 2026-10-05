# examples.verify.math.derived

*Finite set intersection associates.*

**Source.** graham-knuth-patashnik — *Concrete Mathematics*

## Derived fact 1 — (a ∩ b) ∩ c = a ∩ (b ∩ c)

**Coordinate.** Finset · intersection · parentheses do not matter · **Derived fact**

*Source: graham-knuth-patashnik*

*Built on: order does not matter, for intersection on Finset, empty is the left annihilator, for intersection on Finset*

> **Goal.** (a ∩ b) ∩ c = a ∩ (b ∩ c)
>
> $$\forall a \in Finset \forall b \in Finset \forall c \in Finset\quad (a ∩ b) ∩ c = a ∩ (b ∩ c)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that parentheses do not matter for intersection on Finset. |  |  |
| ② | We invoke the derived fact governing intersection on Finset: order does not matter, for intersection on Finset (instantiated for a, b). |  |  |
| ③ | We invoke the derived fact governing intersection on Finset: order does not matter, for intersection on Finset (instantiated for b, c). |  |  |
| ④ | We invoke the definitional clause governing intersection on Finset: empty is the left annihilator, for intersection on Finset (instantiated for c). |  |  |
| ⑤ | From step 2, step 3, and step 4, this implies (a ∩ b) ∩ c equals a ∩ (b ∩ c). Hence proven. | ⑤ | $(a ∩ b) ∩ c = a ∩ (b ∩ c)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ⑤ | step 2, step 3, and step 4 |

`Finset · intersection · parentheses do not matter`
