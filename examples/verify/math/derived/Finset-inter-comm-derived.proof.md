# examples.verify.math.derived

*Intersection commutes as a derived consequence.*

**Source.** graham-knuth-patashnik — *Concrete Mathematics*

## Derived fact 1 — a ∩ b = b ∩ a

**Coordinate.** Finset · intersection · intersection commutes derived · **Derived fact**

*Source: graham-knuth-patashnik*

*Built on: order does not matter, for intersection on Finset*

> **Goal.** a ∩ b = b ∩ a
>
> $$\forall a \in Finset \forall b \in Finset\quad a ∩ b = b ∩ a$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that intersection commutes derived for intersection on Finset. |  |  |
| ② | We invoke the derived fact governing intersection on Finset: order does not matter, for intersection on Finset (instantiated for a, b). |  |  |
| ③ | From step 2, this implies a ∩ b equals b ∩ a. Hence proven. | ③ | $a ∩ b = b ∩ a$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ③ | step 2 |

`Finset · intersection · intersection commutes derived`
