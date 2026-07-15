# examples.verify.math.derived

*True is absorbing for disjunction on the right.*

**Source.** boole — https://en.wikipedia.org/wiki/Boolean_algebra

## Derived fact 1 — a or true = true

**Coordinate.** boolean truth values · disjunction · true is absorbing on the right · **Derived fact**

*Source: boole*

*Built on: order does not matter for "or", true is absorbing on the left, for disjunction on boolean truth values*

> **Goal.** a or true = true
>
> $$\forall a \in \{\mathsf{true}, \mathsf{false}\}\quad a \lor \mathsf{true} = \mathsf{true}$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that true is absorbing on the right for disjunction on boolean truth values. |  |  |
| ② | We invoke the derived fact governing disjunction on boolean truth values: order does not matter for "or" (instantiated for a, true). | ② | $a \lor \mathsf{true} = \mathsf{true} \lor a$ |
| ③ | We invoke the derived fact governing disjunction on boolean truth values: true is absorbing on the left, for disjunction on boolean truth values (instantiated for a). |  |  |
| ④ | From step 2 and step 3, this implies the disjunction of a and true equals true. Hence proven. | ④ | $a \lor \mathsf{true} = \mathsf{true}$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`boolean truth values · disjunction · true is absorbing on the right`
