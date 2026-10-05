# examples.verify.math.derived

*Intersection distributes over union on the left.*

**Source.** graham-knuth-patashnik — *Concrete Mathematics*

## Derived fact 1 — a ∩ (b ∪ c) = (a ∩ b) ∪ (a ∩ c)

**Coordinate.** Finset · intersection · left distribution over union holds · **Derived fact**

*Source: graham-knuth-patashnik*

*Built on: parentheses do not matter, for intersection on Finset, parentheses do not matter, for union on Finset, order does not matter, for intersection on Finset*

> **Goal.** a ∩ (b ∪ c) = (a ∩ b) ∪ (a ∩ c)
>
> $$\forall a \in Finset \forall b \in Finset \forall c \in Finset\quad a ∩ (b ∪ c) = (a ∩ b) ∪ (a ∩ c)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that left distribution over union holds for intersection on Finset. |  |  |
| ② | We invoke the derived fact governing intersection on Finset: parentheses do not matter, for intersection on Finset (instantiated for a, b, c). |  |  |
| ③ | We invoke the derived fact governing union on Finset: parentheses do not matter, for union on Finset (instantiated for a, b, c). |  |  |
| ④ | We invoke the derived fact governing intersection on Finset: order does not matter, for intersection on Finset (instantiated for b, c). |  |  |
| ⑤ | From step 2, step 3, and step 4, this implies a ∩ (b ∪ c) equals (a ∩ b) ∪ (a ∩ c). Hence proven. | ⑤ | $a ∩ (b ∪ c) = (a ∩ b) ∪ (a ∩ c)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ⑤ | step 2, step 3, and step 4 |

`Finset · intersection · left distribution over union holds`
