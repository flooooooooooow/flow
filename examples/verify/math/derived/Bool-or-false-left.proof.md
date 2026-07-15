# examples.verify.math.derived

*False on the left is a disjunctive identity.*

**Source.** boole — https://en.wikipedia.org/wiki/Boolean_algebra

## Derived fact 1 — false or a = a

**Coordinate.** boolean truth values · disjunction · false is the left identity · **Derived fact**

*Source: boole*

*Built on: order does not matter for "or", false is the right identity, for disjunction on boolean truth values*

> **Goal.** false or a = a
>
> $$\forall a \in \{\mathsf{true}, \mathsf{false}\}\quad \mathsf{false} \lor a = a$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that false is the left identity for disjunction on boolean truth values. |  |  |
| ② | We invoke the derived fact governing disjunction on boolean truth values: order does not matter for "or" (instantiated for false, a). | ② | $\mathsf{false} \lor a = a \lor \mathsf{false}$ |
| ③ | We invoke the derived fact governing disjunction on boolean truth values: false is the right identity, for disjunction on boolean truth values (instantiated for a). |  |  |
| ④ | From step 2 and step 3, this implies the disjunction of false and a equals a. Hence proven. | ④ | $\mathsf{false} \lor a = a$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`boolean truth values · disjunction · false is the left identity`
