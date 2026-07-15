# examples.verify.math.derived

*Join above meet via both-side transitivity.*

**Source.** davey-priestley — *Introduction to Lattices and Order*

## Derived fact 1 — join(a, b) >= meet(a, b)

**Coordinate.** Order · lattice · join above meet via both transitivity · **Derived fact**

*Source: davey-priestley*

*Built on: join above meet via transitivity, for lattice on Order, join above meet via left transitivity, for lattice on Order*

> **Goal.** join(a, b) >= meet(a, b)
>
> $$\forall a \in \mathbb{N} \forall b \in \mathbb{N}\quad join(a, b) \ge meet(a, b)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that join above meet via both transitivity for lattice on Order. |  |  |
| ② | We invoke the derived fact governing lattice on Order: join above meet via transitivity, for lattice on Order (instantiated for a, b, join(a, b)). |  |  |
| ③ | We invoke the derived fact governing lattice on Order: join above meet via left transitivity, for lattice on Order (instantiated for a, b). |  |  |
| ④ | From step 2 and step 3, this implies join(a, b) is at least meet(a, b). Hence proven. | ④ | $join(a, b) \ge meet(a, b)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`Order · lattice · join above meet via both transitivity`
