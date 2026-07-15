# examples.verify.math.derived

*Rational multiplication commutes.*

**Source.** landau — *Foundations of Analysis*

## Derived fact 1 — p * q = q * p

**Coordinate.** Rat · multiplication · order does not matter · **Derived fact**

*Source: landau*

*Built on: one is the left identity, for multiplication on Rat, one is the right identity, for multiplication on Rat, order does not matter, for addition on Rat*

> **Goal.** p * q = q * p
>
> $$\forall p \in Rat \forall q \in Rat\quad p \cdot q = q \cdot p$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that order does not matter for multiplication on Rat. |  |  |
| ② | We invoke the definitional clause governing multiplication on Rat: one is the left identity, for multiplication on Rat (instantiated for p). |  |  |
| ③ | We invoke the derived fact governing multiplication on Rat: one is the right identity, for multiplication on Rat (instantiated for q). |  |  |
| ④ | We invoke the derived fact governing addition on Rat: order does not matter, for addition on Rat (instantiated for p, q). |  |  |
| ⑤ | From step 2, step 3, and step 4, this implies p times q equals q times p. Hence proven. | ⑤ | $p \cdot q = q \cdot p$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ⑤ | step 2, step 3, and step 4 |

`Rat · multiplication · order does not matter`
