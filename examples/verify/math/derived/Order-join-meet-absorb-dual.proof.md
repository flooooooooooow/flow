# examples.verify.math.derived

*Dual join meet absorption witness.*

**Source.** davey-priestley — *Introduction to Lattices and Order*

## Derived fact 1 — join(b, meet(b, a)) = join(b, a)

**Coordinate.** Order · lattice · dual join absorbs meet witness · **Derived fact**

*Source: davey-priestley*

*Built on: join absorbs meet derived, for lattice on Order, dual join above meet antisymmetric witness, for lattice on Order*

> **Goal.** join(b, meet(b, a)) = join(b, a)
>
> $$\forall a \in \mathbb{N} \forall b \in \mathbb{N}\quad join(b, meet(b, a)) = join(b, a)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that dual join absorbs meet witness for lattice on Order. |  |  |
| ② | We invoke the derived fact governing lattice on Order: join absorbs meet derived, for lattice on Order (instantiated for b, a). |  |  |
| ③ | We invoke the derived fact governing lattice on Order: dual join above meet antisymmetric witness, for lattice on Order (instantiated for a, b). |  |  |
| ④ | From step 2 and step 3, this implies join(b, meet(b, a)) equals join(b, a). Hence proven. | ④ | $join(b, meet(b, a)) = join(b, a)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`Order · lattice · dual join absorbs meet witness`
