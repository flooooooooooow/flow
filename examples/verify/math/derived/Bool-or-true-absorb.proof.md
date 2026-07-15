# examples.verify.math.derived

*True is absorbing for disjunction on the left.*

**Source.** boole — https://en.wikipedia.org/wiki/Boolean_algebra

## Derived fact 1 — true or a = true

**Coordinate.** boolean truth values · disjunction · true is absorbing on the left · **Derived fact**

*Source: boole*

*Built on: order does not matter for "or"*

> **Goal.** true or a = true
>
> $$\forall a \in \{\mathsf{true}, \mathsf{false}\}\quad \mathsf{true} \lor a = \mathsf{true}$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that true is absorbing on the left for disjunction on boolean truth values. |  |  |
| ② | We split into exhaustive cases — the claim must hold in each one. |  |  |
| ③ | We invoke the derived fact governing disjunction on boolean truth values: order does not matter for "or" (instantiated for true, a). | ③ | $\mathsf{true} \lor a = a \lor \mathsf{true}$ |
| ④ | Case 1 (see step 2): suppose a holds. |  |  |
| ⑤ | From step 4, this implies the disjunction of true and a equals true in this case. | ⑤ | $\mathsf{true} \lor a = \mathsf{true}$ |
| ⑥ | Case 2 (see step 2): neither disjunct holds. |  |  |
| ⑦ | From step 6, this implies the disjunction of true and a equals true. Together with the other cases (step 4 and step 6), the goal is discharged. Hence proven. | ⑦ | $\mathsf{true} \lor a = \mathsf{true}$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 |
| ⑤ | step 4 |
| ⑥ | step 2 |
| ⑦ | step 6 |

`boolean truth values · disjunction · true is absorbing on the left`
