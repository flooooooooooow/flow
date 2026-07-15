# examples.verify.math.derived

*Strict less-than is witnessed by adding a positive amount.*

**Source.** peano — https://en.wikipedia.org/wiki/Total_order

## Derived fact 1 — If a < b then there exists k with a + succ(k) = b

**Coordinate.** the natural numbers · order · strictly below implies a positive right summand · **Derived fact**

*Source: peano — Landau, *Foundations of Analysis**

*Built on: every number is below its successor, for order on the natural numbers, adding zero on the left does not change the number*

> **Goal.** If a < b then there exists k with a + succ(k) = b
>
> $$\forall a \in \mathbb{N} \forall b \in \mathbb{N} \forall k \in \mathbb{N}\quad a < b$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that strictly below implies a positive right summand for order on the natural numbers. |  |  |
| ② | We split into exhaustive cases — the claim must hold in each one. |  |  |
| ③ | Case 1 (see step 2): suppose a < b. |  |  |
| ④ | Case 2 (see step 2): suppose a + succ(k)  equals  b. |  |  |
| ⑤ | We invoke the derived fact governing order on the natural numbers: every number is below its successor, for order on the natural numbers (instantiated for a). |  |  |
| ⑥ | We invoke the definitional clause governing addition on the natural numbers: adding zero on the left does not change the number (instantiated for succ(k)). | ⑥ | $0 + \mathrm{succ}(k) = \mathrm{succ}(k)$ |
| ⑦ | From step 4, step 5, and step 6, this implies a < b. Together with the other cases (step 3 and step 4), the goal is discharged. Hence proven. | ⑦ | $a < b$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ③ | step 2 |
| ④ | step 2 |
| ⑦ | step 4, step 5, and step 6 |

`the natural numbers · order · strictly below implies a positive right summand`
