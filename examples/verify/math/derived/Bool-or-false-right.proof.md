# examples.verify.math.derived

*False on the right is a disjunctive identity.*

**Source.** boole — https://en.wikipedia.org/wiki/Boolean_algebra

## Derived fact 1 — a or false = a

**Coordinate.** boolean truth values · disjunction · false is the right identity from the left · **Derived fact**

*Source: boole*

*Built on: order does not matter for "or", false is the left identity, for disjunction on boolean truth values*

> **Goal.** a or false = a
>
> $$\forall a \in \{\mathsf{true}, \mathsf{false}\}\quad a \lor \mathsf{false} = a$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that false is the right identity from the left for disjunction on boolean truth values. |  |  |
| ② | We invoke the derived fact governing disjunction on boolean truth values: order does not matter for "or" (instantiated for a, false). | ② | $a \lor \mathsf{false} = \mathsf{false} \lor a$ |
| ③ | We invoke the derived fact governing disjunction on boolean truth values: false is the left identity, for disjunction on boolean truth values (instantiated for a). |  |  |
| ④ | From step 2 and step 3, this implies the disjunction of a and false equals a. Hence proven. | ④ | $a \lor \mathsf{false} = a$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`boolean truth values · disjunction · false is the right identity from the left`
