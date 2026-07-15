# examples.verify.math.derived

*Dual meet-below-join commutes in arguments.*

**Source.** davey-priestley — *Introduction to Lattices and Order*

## Derived fact 1 — meet(a, b) <= join(b, a) via dual commutativity

**Coordinate.** Order · lattice · meet below join dual commutes · **Derived fact**

*Source: davey-priestley*

*Built on: meet below join commutes, for lattice on Order, meet below join in dual order, for lattice on Order*

> **Goal.** meet(a, b) <= join(b, a) via dual commutativity
>
> $$\forall a \in \mathbb{N} \forall b \in \mathbb{N}\quad meet(a, b) \le join(b, a)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that meet below join dual commutes for lattice on Order. |  |  |
| ② | We invoke the derived fact governing lattice on Order: meet below join commutes, for lattice on Order (instantiated for a, b). |  |  |
| ③ | We invoke the derived fact governing lattice on Order: meet below join in dual order, for lattice on Order (instantiated for a, b). |  |  |
| ④ | From step 2 and step 3, this implies meet(a, b) is at most join(b, a). Hence proven. | ④ | $meet(a, b) \le join(b, a)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`Order · lattice · meet below join dual commutes`
