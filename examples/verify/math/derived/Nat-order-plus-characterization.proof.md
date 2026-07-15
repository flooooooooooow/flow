# examples.verify.math.derived

*Less-or-equal is characterized by adding a natural on the right.*

**Source.** peano — https://en.wikipedia.org/wiki/Total_order

## Derived fact 1 — a ≤ b if and only if there exists k with a + k = b (forward: addition witness)

**Coordinate.** the natural numbers · order · less-or-equal means a right summand exists · **Derived fact**

*Source: peano — Landau, *Foundations of Analysis**

*Built on: adding on the right preserves order, for addition on the natural numbers*

> **Goal.** a ≤ b if and only if there exists k with a + k = b (forward: addition witness)
>
> $$\forall a \in \mathbb{N} \forall b \in \mathbb{N} \forall k \in \mathbb{N}\quad a \le b$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that less-or-equal means a right summand exists for order on the natural numbers. |  |  |
| ② | We split into exhaustive cases — the claim must hold in each one. |  |  |
| ③ | Case 1 (see step 2): suppose a + k  equals  b. |  |  |
| ④ | We invoke the derived fact governing addition on the natural numbers: adding on the right preserves order, for addition on the natural numbers (instantiated for 0, a, b). |  |  |
| ⑤ | From step 3 and step 4, this implies a is at most b. Together with the other cases (step 3), the goal is discharged. Hence proven. | ⑤ | $a \le b$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ③ | step 2 |
| ⑤ | step 3 and step 4 |

`the natural numbers · order · less-or-equal means a right summand exists`
