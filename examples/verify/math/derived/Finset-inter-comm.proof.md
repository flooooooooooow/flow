# examples.verify.math.derived

*Finite set intersection commutes.*

**Source.** graham-knuth-patashnik — *Concrete Mathematics*

## Derived fact 1 — a ∩ b = b ∩ a

**Coordinate.** Finset · intersection · order does not matter · **Derived fact**

*Source: graham-knuth-patashnik*

*Built on: order does not matter, for union on Finset, empty is the right annihilator, for intersection on Finset*

> **Goal.** a ∩ b = b ∩ a
>
> $$\forall a \in Finset \forall b \in Finset\quad a ∩ b = b ∩ a$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that order does not matter for intersection on Finset. |  |  |
| ② | We invoke the derived fact governing union on Finset: order does not matter, for union on Finset (instantiated for a, b). |  |  |
| ③ | We invoke the definitional clause governing intersection on Finset: empty is the right annihilator, for intersection on Finset (instantiated for a). |  |  |
| ④ | From step 2 and step 3, this implies a ∩ b equals b ∩ a. Hence proven. | ④ | $a ∩ b = b ∩ a$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`Finset · intersection · order does not matter`
