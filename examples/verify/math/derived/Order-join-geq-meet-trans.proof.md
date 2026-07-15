# examples.verify.math.derived

*Join above meet is preserved under transitivity.*

**Source.** davey-priestley — *Introduction to Lattices and Order*

## Derived fact 1 — If meet(a, b) <= c and join(a, b) >= c then join(a, b) >= meet(a, b)

**Coordinate.** Order · lattice · join above meet via transitivity · **Derived fact**

*Source: davey-priestley*

*Built on: meet is below join, for lattice on Order, transitivity holds, for leq on Order*

> **Goal.** If meet(a, b) <= c and join(a, b) >= c then join(a, b) >= meet(a, b)
>
> $$\forall a \in \mathbb{N} \forall b \in \mathbb{N} \forall c \in \mathbb{N}\quad join(a, b) \ge meet(a, b)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that join above meet via transitivity for lattice on Order. |  |  |
| ② | We invoke the derived fact governing lattice on Order: meet is below join, for lattice on Order (instantiated for a, b). |  |  |
| ③ | We invoke the derived fact governing leq on Order: transitivity holds, for leq on Order (instantiated for meet(a, b), c, join(a, b)). |  |  |
| ④ | From step 2 and step 3, this implies join(a, b) is at least meet(a, b). Hence proven. | ④ | $join(a, b) \ge meet(a, b)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`Order · lattice · join above meet via transitivity`
