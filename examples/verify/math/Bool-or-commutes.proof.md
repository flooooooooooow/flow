# Bool-or-commutes

*"A or B" gives the same result as "B or A".*

**Source.** boole — https://en.wikipedia.org/wiki/Boolean_algebra

## Derived fact 1 — "A or B" gives the same result as "B or A"

**Coordinate.** boolean truth values · disjunction · order does not matter · **Derived fact**

*Source: boole — https://en.wikipedia.org/wiki/Boolean_algebra*

> **Goal.** "A or B" gives the same result as "B or A"
>
> $$\forall a \in \{\mathsf{true}, \mathsf{false}\} \forall b \in \{\mathsf{true}, \mathsf{false}\}\quad a \lor b = b \lor a$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that order does not matter for disjunction on boolean truth values. |  |  |
| ② | We split into exhaustive cases — the claim must hold in each one. |  |  |
| ③ | Case 1 (see step 2): suppose a holds. |  |  |
| ④ | From step 3, this implies the disjunction of a and b equals the disjunction of b and a in this case. | ④ | $a \lor b = b \lor a$ |
| ⑤ | Case 2 (see step 2): suppose b holds. |  |  |
| ⑥ | From step 5, this implies the disjunction of a and b equals the disjunction of b and a in this case. | ⑥ | $a \lor b = b \lor a$ |
| ⑦ | Case 3 (see step 2): neither disjunct holds. |  |  |
| ⑧ | From step 7, this implies the disjunction of a and b equals the disjunction of b and a. Together with the other cases (step 3, step 5, and step 7), the goal is discharged. Hence proven. | ⑧ | $a \lor b = b \lor a$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ③ | step 2 |
| ④ | step 3 |
| ⑤ | step 2 |
| ⑥ | step 5 |
| ⑦ | step 2 |
| ⑧ | step 7 |

`boolean truth values · disjunction · order does not matter`
