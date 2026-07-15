# examples.verify.math.derived

*Meet is below join via absorption.*

**Source.** davey-priestley — *Introduction to Lattices and Order*

## Derived fact 1 — meet(a, b) <= join(a, b)

**Coordinate.** Order · lattice · meet is below join via absorption · **Derived fact**

*Source: davey-priestley*

*Built on: meet absorbs join derived, for meet on Order, join absorbs meet derived, for join on Order*

> **Goal.** meet(a, b) <= join(a, b)
>
> $$\forall a \in \mathbb{N} \forall b \in \mathbb{N}\quad meet(a, b) \le join(a, b)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that meet is below join via absorption for lattice on Order. |  |  |
| ② | We invoke the derived fact governing meet on Order: meet absorbs join derived, for meet on Order (instantiated for a, b). |  |  |
| ③ | We invoke the derived fact governing join on Order: join absorbs meet derived, for join on Order (instantiated for a, b). |  |  |
| ④ | From step 2 and step 3, this implies meet(a, b) is at most join(a, b). Hence proven. | ④ | $meet(a, b) \le join(a, b)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`Order · lattice · meet is below join via absorption`
