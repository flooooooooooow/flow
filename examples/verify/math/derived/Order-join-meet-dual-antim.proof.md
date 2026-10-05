# examples.verify.math.derived

*Dual join above meet antisymmetric witness.*

**Source.** davey-priestley — *Introduction to Lattices and Order*

## Derived fact 1 — join(b, a) >= meet(b, a)

**Coordinate.** Order · lattice · dual join above meet antisymmetric witness · **Derived fact**

*Source: davey-priestley*

*Built on: join above meet in dual order, for lattice on Order, join above meet via right transitivity, for lattice on Order*

> **Goal.** join(b, a) >= meet(b, a)
>
> $$\forall a \in \mathbb{N} \forall b \in \mathbb{N}\quad join(b, a) \ge meet(b, a)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that dual join above meet antisymmetric witness for lattice on Order. |  |  |
| ② | We invoke the derived fact governing lattice on Order: join above meet in dual order, for lattice on Order (instantiated for a, b). |  |  |
| ③ | We invoke the derived fact governing lattice on Order: join above meet via right transitivity, for lattice on Order (instantiated for b, a). |  |  |
| ④ | From step 2 and step 3, this implies join(b, a) is at least meet(b, a). Hence proven. | ④ | $join(b, a) \ge meet(b, a)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`Order · lattice · dual join above meet antisymmetric witness`
