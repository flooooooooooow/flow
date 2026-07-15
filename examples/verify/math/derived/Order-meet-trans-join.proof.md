# examples.verify.math.derived

*Meet is below join via transitivity through the left argument.*

**Source.** davey-priestley — *Introduction to Lattices and Order*

## Derived fact 1 — meet(a, b) <= join(a, b)

**Coordinate.** Order · lattice · meet is below join via transitivity · **Derived fact**

*Source: davey-priestley*

*Built on: meet is below the left argument, for meet on Order, join is above the left argument, for join on Order, less-or-equal is transitive, for order on the natural numbers*

> **Goal.** meet(a, b) <= join(a, b)
>
> $$\forall a \in \mathbb{N} \forall b \in \mathbb{N}\quad meet(a, b) \le join(a, b)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that meet is below join via transitivity for lattice on Order. |  |  |
| ② | We split into exhaustive cases — the claim must hold in each one. |  |  |
| ③ | Case 1 (see step 2): suppose meet(a, b) <= a. |  |  |
| ④ | Case 2 (see step 2): suppose a <= join(a, b). |  |  |
| ⑤ | We invoke the derived fact governing meet on Order: meet is below the left argument, for meet on Order (instantiated for a, b). |  |  |
| ⑥ | We invoke the derived fact governing join on Order: join is above the left argument, for join on Order (instantiated for a, b). |  |  |
| ⑦ | We invoke the derived fact governing order on the natural numbers: less-or-equal is transitive, for order on the natural numbers (instantiated for meet(a, b), a, join(a, b)). |  |  |
| ⑧ | From step 4, step 5, step 6, and step 7, this implies meet(a, b) is at most join(a, b). Together with the other cases (step 3 and step 4), the goal is discharged. Hence proven. | ⑧ | $meet(a, b) \le join(a, b)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ③ | step 2 |
| ④ | step 2 |
| ⑧ | step 4, step 5, step 6, and step 7 |

`Order · lattice · meet is below join via transitivity`
