# examples.verify.math.derived

*Equal integers can be subtracted from both sides of an equation.*

**Source.** landau — *Foundations of Analysis*, Ch. 1

## Derived fact 1 — a + c = b + c implies a = b

**Coordinate.** the integers · addition · right cancellation holds · **Derived fact**

*Source: landau*

*Built on: parentheses do not matter, for addition on the integers, negation distributes over addition, for negation on the integers*

> **Goal.** a + c = b + c implies a = b
>
> $$\forall a \in \mathbb{Z} \forall b \in \mathbb{Z} \forall c \in \mathbb{Z}\quad a = b$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that right cancellation holds for addition on the integers. |  |  |
| ② | We split into exhaustive cases — the claim must hold in each one. |  |  |
| ③ | Case 1 (see step 2): suppose a + c  equals  b + c. |  |  |
| ④ | We invoke the derived fact governing addition on the integers: parentheses do not matter, for addition on the integers (instantiated for a, c, -c). |  |  |
| ⑤ | We invoke the derived fact governing negation on the integers: negation distributes over addition, for negation on the integers (instantiated for a, c). |  |  |
| ⑥ | From step 3, step 4, and step 5, this implies a equals b. Together with the other cases (step 3), the goal is discharged. Hence proven. | ⑥ | $a = b$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ③ | step 2 |
| ⑥ | step 3, step 4, and step 5 |

`the integers · addition · right cancellation holds`
