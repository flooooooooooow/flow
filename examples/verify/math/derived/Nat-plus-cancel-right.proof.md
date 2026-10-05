# examples.verify.math.derived

*Equal right summands can be cancelled when they sit on the right.*

**Source.** peano — https://en.wikipedia.org/wiki/Cancellation_property

## Derived fact 1 — From b + a = c + a we deduce b = c

**Coordinate.** the natural numbers · addition · right cancellation holds · **Derived fact**

*Source: peano/induction — Gries & Schneider, Ch. 3*

*Built on: you can swap the order when you add, left cancellation holds, for addition on the natural numbers*

> **Goal.** From b + a = c + a we deduce b = c
>
> $$\forall a \in \mathbb{N} \forall b \in \mathbb{N} \forall c \in \mathbb{N}\quad b = c$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that right cancellation holds for addition on the natural numbers. |  |  |
| ② | We split into exhaustive cases — the claim must hold in each one. |  |  |
| ③ | Case 1 (see step 2): suppose b + a  equals  c + a. |  |  |
| ④ | We invoke the derived fact governing addition on the natural numbers: you can swap the order when you add (instantiated for b, a). | ④ | $b + a = a + b$ |
| ⑤ | We invoke the derived fact governing addition on the natural numbers: you can swap the order when you add (instantiated for c, a). | ⑤ | $c + a = a + c$ |
| ⑥ | We invoke the derived fact governing addition on the natural numbers: left cancellation holds, for addition on the natural numbers (instantiated for a, b, c). |  |  |
| ⑦ | From step 3, step 4, step 5, and step 6, this implies b equals c. Together with the other cases (step 3), the goal is discharged. Hence proven. | ⑦ | $b = c$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ③ | step 2 |
| ⑦ | step 3, step 4, step 5, and step 6 |

`the natural numbers · addition · right cancellation holds`
