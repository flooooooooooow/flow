# examples.verify.math.derived

*Dual meet below join antisymmetric witness.*

**Source.** davey-priestley — *Introduction to Lattices and Order*

## Derived fact 1 — meet(b, a) <= join(b, a)

**Coordinate.** Order · lattice · dual meet below join antisymmetric witness · **Derived fact**

*Source: davey-priestley*

*Built on: meet below join in dual order, for lattice on Order, meet below join via left transitivity, for lattice on Order*

> **Goal.** meet(b, a) <= join(b, a)
>
> $$\forall a \in \mathbb{N} \forall b \in \mathbb{N}\quad meet(b, a) \le join(b, a)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that dual meet below join antisymmetric witness for lattice on Order. |  |  |
| ② | We invoke the derived fact governing lattice on Order: meet below join in dual order, for lattice on Order (instantiated for a, b). |  |  |
| ③ | We invoke the derived fact governing lattice on Order: meet below join via left transitivity, for lattice on Order (instantiated for b, a). |  |  |
| ④ | From step 2 and step 3, this implies meet(b, a) is at most join(b, a). Hence proven. | ④ | $meet(b, a) \le join(b, a)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`Order · lattice · dual meet below join antisymmetric witness`
