# examples.verify.math.derived

*Meet is below join via idempotence.*

**Source.** davey-priestley — *Introduction to Lattices and Order*

## Derived fact 1 — meet(a, b) <= join(a, b)

**Coordinate.** Order · lattice · meet is below join via idempotence · **Derived fact**

*Source: davey-priestley*

*Built on: meet is below join, for lattice on Order, repeating does not change the value, for meet on Order*

> **Goal.** meet(a, b) <= join(a, b)
>
> $$\forall a \in \mathbb{N} \forall b \in \mathbb{N}\quad meet(a, b) \le join(a, b)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that meet is below join via idempotence for lattice on Order. |  |  |
| ② | We invoke the derived fact governing lattice on Order: meet is below join, for lattice on Order (instantiated for a, b). |  |  |
| ③ | We invoke the derived fact governing meet on Order: repeating does not change the value, for meet on Order (instantiated for a). |  |  |
| ④ | From step 2 and step 3, this implies meet(a, b) is at most join(a, b). Hence proven. | ④ | $meet(a, b) \le join(a, b)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`Order · lattice · meet is below join via idempotence`
