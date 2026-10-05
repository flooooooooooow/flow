# examples.verify.math.derived

*Zero on the right annihilates rational multiplication.*

**Source.** landau — *Foundations of Analysis*

## Derived fact 1 — q * 0 = 0

**Coordinate.** Rat · multiplication · zero on the right gives zero · **Derived fact**

*Source: landau*

*Built on: zero on the left gives zero, for multiplication on Rat, order does not matter, for multiplication on Rat*

> **Goal.** q * 0 = 0
>
> $$\forall q \in Rat\quad q \cdot 0 = 0$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that zero on the right gives zero for multiplication on Rat. |  |  |
| ② | We invoke the derived fact governing multiplication on Rat: zero on the left gives zero, for multiplication on Rat (instantiated for q). |  |  |
| ③ | We invoke the derived fact governing multiplication on Rat: order does not matter, for multiplication on Rat (instantiated for q, 0). |  |  |
| ④ | From step 2 and step 3, this implies q times 0 equals 0. Hence proven. | ④ | $q \cdot 0 = 0$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`Rat · multiplication · zero on the right gives zero`
