# examples.verify.math.derived

*Dual meet join absorption witness.*

**Source.** davey-priestley — *Introduction to Lattices and Order*

## Derived fact 1 — meet(b, join(b, a)) = meet(b, a)

**Coordinate.** Order · lattice · dual meet absorbs join witness · **Derived fact**

*Source: davey-priestley*

*Built on: meet absorbs join derived, for lattice on Order, dual meet below join antisymmetric witness, for lattice on Order*

> **Goal.** meet(b, join(b, a)) = meet(b, a)
>
> $$\forall a \in \mathbb{N} \forall b \in \mathbb{N}\quad meet(b, join(b, a)) = meet(b, a)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that dual meet absorbs join witness for lattice on Order. |  |  |
| ② | We invoke the derived fact governing lattice on Order: meet absorbs join derived, for lattice on Order (instantiated for b, a). |  |  |
| ③ | We invoke the derived fact governing lattice on Order: dual meet below join antisymmetric witness, for lattice on Order (instantiated for a, b). |  |  |
| ④ | From step 2 and step 3, this implies meet(b, join(b, a)) equals meet(b, a). Hence proven. | ④ | $meet(b, join(b, a)) = meet(b, a)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`Order · lattice · dual meet absorbs join witness`
