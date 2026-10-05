# examples.verify.math.derived

*Meet below join is preserved under transitivity.*

**Source.** davey-priestley — *Introduction to Lattices and Order*

## Derived fact 1 — If meet(a, b) <= c and c <= join(a, b) then meet(a, b) <= join(a, b)

**Coordinate.** Order · lattice · meet below join via transitivity · **Derived fact**

*Source: davey-priestley*

*Built on: meet is below join, for lattice on Order, transitivity holds, for leq on Order*

> **Goal.** If meet(a, b) <= c and c <= join(a, b) then meet(a, b) <= join(a, b)
>
> $$\forall a \in \mathbb{N} \forall b \in \mathbb{N} \forall c \in \mathbb{N}\quad meet(a, b) \le join(a, b)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that meet below join via transitivity for lattice on Order. |  |  |
| ② | We invoke the derived fact governing lattice on Order: meet is below join, for lattice on Order (instantiated for a, b). |  |  |
| ③ | We invoke the derived fact governing leq on Order: transitivity holds, for leq on Order (instantiated for meet(a, b), c, join(a, b)). |  |  |
| ④ | From step 2 and step 3, this implies meet(a, b) is at most join(a, b). Hence proven. | ④ | $meet(a, b) \le join(a, b)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`Order · lattice · meet below join via transitivity`
