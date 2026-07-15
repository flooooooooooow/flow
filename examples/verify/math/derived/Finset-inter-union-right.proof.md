# examples.verify.math.derived

*Intersection distributes over union on the right.*

**Source.** graham-knuth-patashnik — *Concrete Mathematics*

## Derived fact 1 — (b ∪ c) ∩ a = (b ∩ a) ∪ (c ∩ a)

**Coordinate.** Finset · intersection · right distribution over union holds · **Derived fact**

*Source: graham-knuth-patashnik*

*Built on: left distribution over union holds, for intersection on Finset, order does not matter, for intersection on Finset*

> **Goal.** (b ∪ c) ∩ a = (b ∩ a) ∪ (c ∩ a)
>
> $$\forall a \in Finset \forall b \in Finset \forall c \in Finset\quad (b ∪ c) ∩ a = (b ∩ a) ∪ (c ∩ a)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that right distribution over union holds for intersection on Finset. |  |  |
| ② | We invoke the derived fact governing intersection on Finset: left distribution over union holds, for intersection on Finset (instantiated for a, b, c). |  |  |
| ③ | We invoke the derived fact governing intersection on Finset: order does not matter, for intersection on Finset (instantiated for b, c). |  |  |
| ④ | From step 2 and step 3, this implies (b ∪ c) ∩ a equals (b ∩ a) ∪ (c ∩ a). Hence proven. | ④ | $(b ∪ c) ∩ a = (b ∩ a) ∪ (c ∩ a)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`Finset · intersection · right distribution over union holds`
