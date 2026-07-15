# examples.verify.math.derived

*Equal reals can be subtracted from both sides.*

**Source.** landau — *Foundations of Analysis*

## Derived fact 1 — x + z = y + z implies x = y

**Coordinate.** the real numbers · addition · right cancellation holds · **Derived fact**

*Source: landau*

*Built on: parentheses do not matter, for addition on the real numbers, zero is the right identity, for addition on the real numbers*

> **Goal.** x + z = y + z implies x = y
>
> $$\forall x \in \mathbb{R} \forall y \in \mathbb{R} \forall z \in \mathbb{R}\quad x = y$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that right cancellation holds for addition on the real numbers. |  |  |
| ② | We split into exhaustive cases — the claim must hold in each one. |  |  |
| ③ | Case 1 (see step 2): suppose x + z  equals  y + z. |  |  |
| ④ | We invoke the derived fact governing addition on the real numbers: parentheses do not matter, for addition on the real numbers (instantiated for x, z, -z). |  |  |
| ⑤ | We invoke the definitional clause governing addition on the real numbers: zero is the right identity, for addition on the real numbers (instantiated for x). |  |  |
| ⑥ | From step 3, step 4, and step 5, this implies x equals y. Together with the other cases (step 3), the goal is discharged. Hence proven. | ⑥ | $x = y$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ③ | step 2 |
| ⑥ | step 3, step 4, and step 5 |

`the real numbers · addition · right cancellation holds`
