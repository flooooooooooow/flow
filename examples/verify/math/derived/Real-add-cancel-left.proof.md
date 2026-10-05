# examples.verify.math.derived

*Equal reals can be subtracted from the left of both sides.*

**Source.** landau — *Foundations of Analysis*

## Derived fact 1 — z + x = z + y implies x = y

**Coordinate.** the real numbers · addition · left cancellation holds · **Derived fact**

*Source: landau*

*Built on: right cancellation holds, for addition on the real numbers, order does not matter, for addition on the real numbers*

> **Goal.** z + x = z + y implies x = y
>
> $$\forall x \in \mathbb{R} \forall y \in \mathbb{R} \forall z \in \mathbb{R}\quad x = y$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that left cancellation holds for addition on the real numbers. |  |  |
| ② | We split into exhaustive cases — the claim must hold in each one. |  |  |
| ③ | Case 1 (see step 2): suppose z + x  equals  z + y. |  |  |
| ④ | We invoke the derived fact governing addition on the real numbers: right cancellation holds, for addition on the real numbers (instantiated for x, y, z). |  |  |
| ⑤ | We invoke the derived fact governing addition on the real numbers: order does not matter, for addition on the real numbers (instantiated for z, x). |  |  |
| ⑥ | From step 3, step 4, and step 5, this implies x equals y. Together with the other cases (step 3), the goal is discharged. Hence proven. | ⑥ | $x = y$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ③ | step 2 |
| ⑥ | step 3, step 4, and step 5 |

`the real numbers · addition · left cancellation holds`
