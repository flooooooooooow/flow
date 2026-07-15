# examples.verify.math.derived

*Meet below join via left transitivity witness.*

**Source.** davey-priestley — *Introduction to Lattices and Order*

## Derived fact 1 — meet(a, b) <= join(a, b)

**Coordinate.** Order · lattice · meet below join via left transitivity · **Derived fact**

*Source: davey-priestley*

*Built on: meet below join reflexive, for lattice on Order, transitivity holds, for leq on Order*

> **Goal.** meet(a, b) <= join(a, b)
>
> $$\forall a \in \mathbb{N} \forall b \in \mathbb{N}\quad meet(a, b) \le join(a, b)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that meet below join via left transitivity for lattice on Order. |  |  |
| ② | We invoke the derived fact governing lattice on Order: meet below join reflexive, for lattice on Order (instantiated for a). |  |  |
| ③ | We invoke the derived fact governing leq on Order: transitivity holds, for leq on Order (instantiated for meet(a, b), meet(a, b), join(a, b)). |  |  |
| ④ | From step 2 and step 3, this implies meet(a, b) is at most join(a, b). Hence proven. | ④ | $meet(a, b) \le join(a, b)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`Order · lattice · meet below join via left transitivity`
