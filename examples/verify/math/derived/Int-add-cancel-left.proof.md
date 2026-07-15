# examples.verify.math.derived

*Equal integers can be subtracted from the left of both sides.*

**Source.** landau — *Foundations of Analysis*, Ch. 1

## Derived fact 1 — c + a = c + b implies a = b

**Coordinate.** the integers · addition · left cancellation holds · **Derived fact**

*Source: landau*

*Built on: right cancellation holds, for addition on the integers, order does not matter, for addition on the integers*

> **Goal.** c + a = c + b implies a = b
>
> $$\forall a \in \mathbb{Z} \forall b \in \mathbb{Z} \forall c \in \mathbb{Z}\quad a = b$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that left cancellation holds for addition on the integers. |  |  |
| ② | We split into exhaustive cases — the claim must hold in each one. |  |  |
| ③ | Case 1 (see step 2): suppose c + a  equals  c + b. |  |  |
| ④ | We invoke the derived fact governing addition on the integers: right cancellation holds, for addition on the integers (instantiated for a, b, c). |  |  |
| ⑤ | We invoke the derived fact governing addition on the integers: order does not matter, for addition on the integers (instantiated for c, a). |  |  |
| ⑥ | From step 3, step 4, and step 5, this implies a equals b. Together with the other cases (step 3), the goal is discharged. Hence proven. | ⑥ | $a = b$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ③ | step 2 |
| ⑥ | step 3, step 4, and step 5 |

`the integers · addition · left cancellation holds`
