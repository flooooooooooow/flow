# examples.verify.math.derived

*False is absorbing for conjunction on the left.*

**Source.** boole — https://en.wikipedia.org/wiki/Boolean_algebra

## Derived fact 1 — false and a = false

**Coordinate.** boolean truth values · conjunction · false is absorbing on the left · **Derived fact**

*Source: boole*

*Built on: order does not matter, for conjunction on boolean truth values*

> **Goal.** false and a = false
>
> $$\forall a \in \{\mathsf{true}, \mathsf{false}\}\quad \mathsf{false} \land a = \mathsf{false}$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that false is absorbing on the left for conjunction on boolean truth values. |  |  |
| ② | We split into exhaustive cases — the claim must hold in each one. |  |  |
| ③ | We invoke the derived fact governing conjunction on boolean truth values: order does not matter, for conjunction on boolean truth values (instantiated for false, a). |  |  |
| ④ | Case 1 (see step 2): suppose a holds. |  |  |
| ⑤ | From step 4, this implies the conjunction of false and a equals false in this case. | ⑤ | $\mathsf{false} \land a = \mathsf{false}$ |
| ⑥ | Case 2 (see step 2): neither disjunct holds. |  |  |
| ⑦ | From step 6, this implies the conjunction of false and a equals false. Together with the other cases (step 4 and step 6), the goal is discharged. Hence proven. | ⑦ | $\mathsf{false} \land a = \mathsf{false}$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 |
| ⑤ | step 4 |
| ⑥ | step 2 |
| ⑦ | step 6 |

`boolean truth values · conjunction · false is absorbing on the left`
