# examples.verify.math.derived

*Equal rationals can be subtracted from the left.*

**Source.** landau — *Foundations of Analysis*

## Derived fact 1 — r + p = r + q implies p = q

**Coordinate.** Rat · addition · left cancellation holds · **Derived fact**

*Source: landau*

*Built on: right cancellation holds, for addition on Rat, order does not matter, for addition on Rat*

> **Goal.** r + p = r + q implies p = q
>
> $$\forall p \in Rat \forall q \in Rat \forall r \in Rat\quad p = q$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that left cancellation holds for addition on Rat. |  |  |
| ② | We split into exhaustive cases — the claim must hold in each one. |  |  |
| ③ | Case 1 (see step 2): suppose r + p  equals  r + q. |  |  |
| ④ | We invoke the derived fact governing addition on Rat: right cancellation holds, for addition on Rat (instantiated for p, q, r). |  |  |
| ⑤ | We invoke the derived fact governing addition on Rat: order does not matter, for addition on Rat (instantiated for r, p). |  |  |
| ⑥ | From step 3, step 4, and step 5, this implies p equals q. Together with the other cases (step 3), the goal is discharged. Hence proven. | ⑥ | $p = q$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ③ | step 2 |
| ⑥ | step 3, step 4, and step 5 |

`Rat · addition · left cancellation holds`
