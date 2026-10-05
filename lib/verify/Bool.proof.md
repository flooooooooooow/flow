# verify.Bool

*Boolean algebra lemmas for disjunction and conjunction.*

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

## Derived fact 2 — "A and B" gives the same result as "B and A"

**Coordinate.** boolean truth values · conjunction · order does not matter · **Derived fact**

*Source: boole — https://en.wikipedia.org/wiki/Boolean_algebra*

*Built on: order does not matter for "or"*

> **Goal.** "A and B" gives the same result as "B and A"
>
> $$\forall a \in \{\mathsf{true}, \mathsf{false}\} \forall b \in \{\mathsf{true}, \mathsf{false}\}\quad a \land b = b \land a$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that order does not matter for conjunction on boolean truth values. |  |  |
| ② | We split into exhaustive cases — the claim must hold in each one. |  |  |
| ③ | Case 1 (see step 2): suppose a holds. |  |  |
| ④ | Case 2 (see step 2): suppose b holds. |  |  |
| ⑤ | From step 4, this implies the conjunction of a and b equals the conjunction of b and a in this case. | ⑤ | $a \land b = b \land a$ |
| ⑥ | Case 3 (see step 2): neither disjunct holds. |  |  |
| ⑦ | From step 6, this implies the conjunction of a and b equals the conjunction of b and a in this case. | ⑦ | $a \land b = b \land a$ |
| ⑧ | Case 4 (see step 2): suppose b holds. |  |  |
| ⑨ | From step 8, this implies the conjunction of a and b equals the conjunction of b and a in this case. | ⑨ | $a \land b = b \land a$ |
| ⑩ | Case 5 (see step 2): neither disjunct holds. |  |  |
| ⑪ | From step 10, this implies the conjunction of a and b equals the conjunction of b and a. Together with the other cases (step 3, step 4, step 6, step 8, and step 10), the goal is discharged. Hence proven. | ⑪ | $a \land b = b \land a$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ③ | step 2 |
| ④ | step 2 |
| ⑤ | step 4 |
| ⑥ | step 2 |
| ⑦ | step 6 |
| ⑧ | step 2 |
| ⑨ | step 8 |
| ⑩ | step 2 |
| ⑪ | step 10 |

`boolean truth values · conjunction · order does not matter`

## Derived fact 3 — Or with false on the right leaves the left value unchanged

**Coordinate.** boolean truth values · disjunction · false is the right identity · **Derived fact**

*Source: boole — https://en.wikipedia.org/wiki/Identity_element*

> **Goal.** Or with false on the right leaves the left value unchanged
>
> $$\forall a \in \{\mathsf{true}, \mathsf{false}\}\quad a \lor \mathsf{false} = a$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that false is the right identity for disjunction on boolean truth values. |  |  |
| ② | We split into exhaustive cases — the claim must hold in each one. |  |  |
| ③ | Case 1 (see step 2): suppose a holds. |  |  |
| ④ | From step 3, this implies the disjunction of a and false equals a in this case. | ④ | $a \lor \mathsf{false} = a$ |
| ⑤ | Case 2 (see step 2): neither disjunct holds. |  |  |
| ⑥ | From step 5, this implies the disjunction of a and false equals a. Together with the other cases (step 3 and step 5), the goal is discharged. Hence proven. | ⑥ | $a \lor \mathsf{false} = a$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ③ | step 2 |
| ④ | step 3 |
| ⑤ | step 2 |
| ⑥ | step 5 |

`boolean truth values · disjunction · false is the right identity`

## Derived fact 4 — And with true on the right leaves the left value unchanged

**Coordinate.** boolean truth values · conjunction · true is the right identity · **Derived fact**

*Source: boole — https://en.wikipedia.org/wiki/Identity_element*

> **Goal.** And with true on the right leaves the left value unchanged
>
> $$\forall a \in \{\mathsf{true}, \mathsf{false}\}\quad a \land \mathsf{true} = a$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that true is the right identity for conjunction on boolean truth values. |  |  |
| ② | We split into exhaustive cases — the claim must hold in each one. |  |  |
| ③ | Case 1 (see step 2): suppose a holds. |  |  |
| ④ | From step 3, this implies the conjunction of a and true equals a in this case. | ④ | $a \land \mathsf{true} = a$ |
| ⑤ | Case 2 (see step 2): neither disjunct holds. |  |  |
| ⑥ | From step 5, this implies the conjunction of a and true equals a. Together with the other cases (step 3 and step 5), the goal is discharged. Hence proven. | ⑥ | $a \land \mathsf{true} = a$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ③ | step 2 |
| ④ | step 3 |
| ⑤ | step 2 |
| ⑥ | step 5 |

`boolean truth values · conjunction · true is the right identity`
