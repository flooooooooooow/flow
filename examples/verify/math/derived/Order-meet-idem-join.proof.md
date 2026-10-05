# examples.verify.math.derived

*Meet of meet and join is idempotent on the left.*

**Source.** davey-priestley — *Introduction to Lattices and Order*

## Derived fact 1 — meet(meet(a, b), join(a, b)) = meet(a, b)

**Coordinate.** Order · lattice · meet idempotent with join · **Derived fact**

*Source: davey-priestley*

*Built on: meet absorbs join derived, for lattice on Order, repeating does not change the value, for meet on Order*

> **Goal.** meet(meet(a, b), join(a, b)) = meet(a, b)
>
> $$\forall a \in \mathbb{N} \forall b \in \mathbb{N}\quad meet(meet(a, b), join(a, b)) = meet(a, b)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that meet idempotent with join for lattice on Order. |  |  |
| ② | We invoke the derived fact governing lattice on Order: meet absorbs join derived, for lattice on Order (instantiated for a, b). |  |  |
| ③ | We invoke the derived fact governing meet on Order: repeating does not change the value, for meet on Order (instantiated for meet(a, b)). |  |  |
| ④ | From step 2 and step 3, this implies meet(meet(a, b), join(a, b)) equals meet(a, b). Hence proven. | ④ | $meet(meet(a, b), join(a, b)) = meet(a, b)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`Order · lattice · meet idempotent with join`
