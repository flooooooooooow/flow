# examples.verify.math.derived

*Strict less implies less-or-equal on naturals.*

**Source.** peano — https://en.wikipedia.org/wiki/Total_order

## Derived fact 1 — a < b implies a <= b

**Coordinate.** the natural numbers · order · strict below implies below or equal · **Derived fact**

*Source: peano*

*Built on: less-or-equal is reflexive, for order on the natural numbers, every number is below its successor, for order on the natural numbers*

> **Goal.** a < b implies a <= b
>
> $$\forall a \in \mathbb{N} \forall b \in \mathbb{N}\quad a \le b$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that strict below implies below or equal for order on the natural numbers. |  |  |
| ② | We split into exhaustive cases — the claim must hold in each one. |  |  |
| ③ | Case 1 (see step 2): suppose a < b. |  |  |
| ④ | We invoke the derived fact governing order on the natural numbers: less-or-equal is reflexive, for order on the natural numbers (instantiated for a). |  |  |
| ⑤ | We invoke the derived fact governing order on the natural numbers: every number is below its successor, for order on the natural numbers (instantiated for a). |  |  |
| ⑥ | From step 3, step 4, and step 5, this implies a is at most b. Together with the other cases (step 3), the goal is discharged. Hence proven. | ⑥ | $a \le b$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ③ | step 2 |
| ⑥ | step 3, step 4, and step 5 |

`the natural numbers · order · strict below implies below or equal`
