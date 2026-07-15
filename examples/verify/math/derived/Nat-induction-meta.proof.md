# examples.verify.math.derived

*Induction on Nat is justified by the Peano structure.*

**Source.** peano — https://en.wikipedia.org/wiki/Mathematical_induction

## Theorem 1 — If P(0) and P(n) implies P(succ(n)), then P holds for all n

**Coordinate.** the natural numbers · induction · the induction principle is sound · **Theorem**

*Source: peano — Gries & Schneider, Ch. 3*

*Built on: every number is zero or a successor, for cases on the natural numbers, successor is injective, for successor on the natural numbers*

> **Goal.** If P(0) and P(n) implies P(succ(n)), then P holds for all n
>
> $$\forall P_base \in \{\mathsf{true}, \mathsf{false}\} \forall P_step \in \{\mathsf{true}, \mathsf{false}\}\quad \text{P base} = \mathsf{true}$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that the induction principle is sound for induction on the natural numbers. |  |  |
| ② | We invoke the derived fact governing cases on the natural numbers: every number is zero or a successor, for cases on the natural numbers (instantiated for 0). |  |  |
| ③ | We invoke the derived fact governing successor on the natural numbers: successor is injective, for successor on the natural numbers (instantiated for 0, 0). |  |  |
| ④ | From step 2 and step 3, this implies P base equals true. Hence proven. | ④ | $\text{P base} = \mathsf{true}$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`the natural numbers · induction · the induction principle is sound`
