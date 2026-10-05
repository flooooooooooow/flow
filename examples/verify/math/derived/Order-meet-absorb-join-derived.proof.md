# examples.verify.math.derived

*Meet absorbs into join in a lattice witness.*

**Source.** davey-priestley — *Introduction to Lattices and Order*

## Derived fact 1 — meet(a, join(a, b)) = meet(a, b)

**Coordinate.** Order · lattice · meet absorbs join derived · **Derived fact**

*Source: davey-priestley*

*Built on: meet absorbs join on the left, for lattice on Order, meet is below the left argument, for meet on Order*

> **Goal.** meet(a, join(a, b)) = meet(a, b)
>
> $$\forall a \in \mathbb{N} \forall b \in \mathbb{N}\quad meet(a, join(a, b)) = meet(a, b)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that meet absorbs join derived for lattice on Order. |  |  |
| ② | We invoke the derived fact governing lattice on Order: meet absorbs join on the left, for lattice on Order (instantiated for a, b). |  |  |
| ③ | We invoke the derived fact governing meet on Order: meet is below the left argument, for meet on Order (instantiated for a, b). |  |  |
| ④ | From step 2 and step 3, this implies meet(a, join(a, b)) equals meet(a, b). Hence proven. | ④ | $meet(a, join(a, b)) = meet(a, b)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`Order · lattice · meet absorbs join derived`
