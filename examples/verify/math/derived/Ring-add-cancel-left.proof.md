# examples.verify.math.derived

*Equal ring elements can be subtracted from the left.*

**Source.** dummit-foote — *Abstract Algebra*, §7.1

## Derived fact 1 — c + a = c + b implies a = b

**Coordinate.** Ring · addition · left cancellation holds · **Derived fact**

*Source: dummit-foote*

*Built on: right cancellation holds, for addition on Ring, order does not matter, for addition on Ring*

> **Goal.** c + a = c + b implies a = b
>
> $$\forall a \in Ring \forall b \in Ring \forall c \in Ring\quad a = b$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that left cancellation holds for addition on Ring. |  |  |
| ② | We split into exhaustive cases — the claim must hold in each one. |  |  |
| ③ | Case 1 (see step 2): suppose c + a  equals  c + b. |  |  |
| ④ | We invoke the derived fact governing addition on Ring: right cancellation holds, for addition on Ring (instantiated for a, b, c). |  |  |
| ⑤ | We invoke the definitional clause governing addition on Ring: order does not matter, for addition on Ring (instantiated for c, a). |  |  |
| ⑥ | From step 3, step 4, and step 5, this implies a equals b. Together with the other cases (step 3), the goal is discharged. Hence proven. | ⑥ | $a = b$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ③ | step 2 |
| ⑥ | step 3, step 4, and step 5 |

`Ring · addition · left cancellation holds`
