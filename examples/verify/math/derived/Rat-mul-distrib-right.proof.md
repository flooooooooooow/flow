# examples.verify.math.derived

*Rational multiplication distributes over addition on the right.*

**Source.** landau — *Foundations of Analysis*

## Derived fact 1 — (q + r) * p = q * p + r * p

**Coordinate.** Rat · multiplication · right distribution over addition holds · **Derived fact**

*Source: landau*

*Built on: left distribution over addition holds, for multiplication on Rat, order does not matter, for multiplication on Rat*

> **Goal.** (q + r) * p = q * p + r * p
>
> $$\forall p \in Rat \forall q \in Rat \forall r \in Rat\quad (q + r) * p = q \cdot p + r \cdot p$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that right distribution over addition holds for multiplication on Rat. |  |  |
| ② | We invoke the derived fact governing multiplication on Rat: left distribution over addition holds, for multiplication on Rat (instantiated for p, q, r). |  |  |
| ③ | We invoke the derived fact governing multiplication on Rat: order does not matter, for multiplication on Rat (instantiated for q, p). |  |  |
| ④ | We invoke the derived fact governing multiplication on Rat: order does not matter, for multiplication on Rat (instantiated for r, p). |  |  |
| ⑤ | From step 2, step 3, and step 4, this implies (q plus r) times p equals q times p plus r times p. Hence proven. | ⑤ | $(q + r) * p = q \cdot p + r \cdot p$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ⑤ | step 2, step 3, and step 4 |

`Rat · multiplication · right distribution over addition holds`
