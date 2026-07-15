# examples.verify.math.derived

*Any two naturals are comparable by less-or-equal in one direction.*

**Source.** peano — https://en.wikipedia.org/wiki/Trichotomy_(mathematics)

## Derived fact 1 — For all a and b, either a ≤ b or b ≤ a

**Coordinate.** the natural numbers · order · one side is less than or equal to the other · **Derived fact**

*Source: peano/induction — Gries & Schneider, Ch. 3*

*Built on: less-or-equal is reflexive, for order on the natural numbers, less-or-equal is transitive, for order on the natural numbers, every number is below its successor, for order on the natural numbers*

> **Goal.** For all a and b, either a ≤ b or b ≤ a
>
> $$\forall a \in \mathbb{N} \forall b \in \mathbb{N}\quad b \le a$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that one side is less than or equal to the other for order on the natural numbers. |  |  |
| ② | We split into exhaustive cases — the claim must hold in each one. |  |  |
| ③ | Case 1 (see step 2): suppose a  equals  b. |  |  |
| ④ | We invoke the derived fact governing order on the natural numbers: less-or-equal is reflexive, for order on the natural numbers (instantiated for a). |  |  |
| ⑤ | From step 3 and step 4, this implies a is at most b in this case. | ⑤ | $a \le b$ |
| ⑥ | Case 2 (see step 2): suppose a < b. |  |  |
| ⑦ | From step 6, this implies a is at most b in this case. | ⑦ | $a \le b$ |
| ⑧ | Case 3 (see step 2): neither disjunct holds. |  |  |
| ⑨ | We invoke the derived fact governing order on the natural numbers: less-or-equal is reflexive, for order on the natural numbers (instantiated for b). |  |  |
| ⑩ | From step 8 and step 9, this implies b is at most a. Together with the other cases (step 3, step 6, and step 8), the goal is discharged. Hence proven. | ⑩ | $b \le a$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ③ | step 2 |
| ⑤ | step 3 and step 4 |
| ⑥ | step 2 |
| ⑦ | step 6 |
| ⑧ | step 2 |
| ⑩ | step 8 and step 9 |

`the natural numbers · order · one side is less than or equal to the other`
