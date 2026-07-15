# examples.verify.math.derived

*Equal rationals can be subtracted from both sides.*

**Source.** landau — *Foundations of Analysis*

## Derived fact 1 — p + r = q + r implies p = q

**Coordinate.** Rat · addition · right cancellation holds · **Derived fact**

*Source: landau*

*Built on: parentheses do not matter, for addition on Rat, zero is the right identity, for addition on Rat*

> **Goal.** p + r = q + r implies p = q
>
> $$\forall p \in Rat \forall q \in Rat \forall r \in Rat\quad p = q$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that right cancellation holds for addition on Rat. |  |  |
| ② | We split into exhaustive cases — the claim must hold in each one. |  |  |
| ③ | Case 1 (see step 2): suppose p + r  equals  q + r. |  |  |
| ④ | We invoke the derived fact governing addition on Rat: parentheses do not matter, for addition on Rat (instantiated for p, r, -r). |  |  |
| ⑤ | We invoke the definitional clause governing addition on Rat: zero is the right identity, for addition on Rat (instantiated for p). |  |  |
| ⑥ | From step 3, step 4, and step 5, this implies p equals q. Together with the other cases (step 3), the goal is discharged. Hence proven. | ⑥ | $p = q$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ③ | step 2 |
| ⑥ | step 3, step 4, and step 5 |

`Rat · addition · right cancellation holds`
