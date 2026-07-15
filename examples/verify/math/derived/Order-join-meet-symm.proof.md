# examples.verify.math.derived

*Join above meet is symmetric in arguments.*

**Source.** davey-priestley — *Introduction to Lattices and Order*

## Derived fact 1 — join(a, b) >= meet(b, a)

**Coordinate.** Order · lattice · join above meet symmetric · **Derived fact**

*Source: davey-priestley*

*Built on: join above meet via both transitivity, for lattice on Order, meet commutes, for meet on Order*

> **Goal.** join(a, b) >= meet(b, a)
>
> $$\forall a \in \mathbb{N} \forall b \in \mathbb{N}\quad join(a, b) \ge meet(b, a)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that join above meet symmetric for lattice on Order. |  |  |
| ② | We invoke the derived fact governing lattice on Order: join above meet via both transitivity, for lattice on Order (instantiated for a, b). |  |  |
| ③ | We invoke the derived fact governing meet on Order: meet commutes, for meet on Order (instantiated for a, b). |  |  |
| ④ | From step 2 and step 3, this implies join(a, b) is at least meet(b, a). Hence proven. | ④ | $join(a, b) \ge meet(b, a)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`Order · lattice · join above meet symmetric`
