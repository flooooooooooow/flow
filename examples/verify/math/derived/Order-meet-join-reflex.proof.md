# examples.verify.math.derived

*Meet below join is reflexive on equal arguments.*

**Source.** davey-priestley — *Introduction to Lattices and Order*

## Derived fact 1 — meet(a, a) <= join(a, a)

**Coordinate.** Order · lattice · meet below join reflexive · **Derived fact**

*Source: davey-priestley*

*Built on: meet below join commutes, for lattice on Order, repeating does not change the value, for meet on Order*

> **Goal.** meet(a, a) <= join(a, a)
>
> $$\forall a \in \mathbb{N}\quad meet(a, a) \le join(a, a)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that meet below join reflexive for lattice on Order. |  |  |
| ② | We invoke the derived fact governing lattice on Order: meet below join commutes, for lattice on Order (instantiated for a, a). |  |  |
| ③ | We invoke the derived fact governing meet on Order: repeating does not change the value, for meet on Order (instantiated for a). |  |  |
| ④ | From step 2 and step 3, this implies meet(a, a) is at most join(a, a). Hence proven. | ④ | $meet(a, a) \le join(a, a)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`Order · lattice · meet below join reflexive`
