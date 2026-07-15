# examples.verify.math.derived

*Meet with itself returns the argument.*

**Source.** davey-priestley — *Introduction to Lattices and Order*

## Derived fact 1 — meet(a, a) = a

**Coordinate.** Order · meet · meet with itself equals the argument · **Derived fact**

*Source: davey-priestley*

*Built on: repeating does not change the value, for meet on Order, less-or-equal is reflexive, for order on the natural numbers*

> **Goal.** meet(a, a) = a
>
> $$\forall a \in \mathbb{N}\quad meet(a, a) = a$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that meet with itself equals the argument for meet on Order. |  |  |
| ② | We invoke the derived fact governing meet on Order: repeating does not change the value, for meet on Order (instantiated for a). |  |  |
| ③ | We invoke the derived fact governing order on the natural numbers: less-or-equal is reflexive, for order on the natural numbers (instantiated for a). |  |  |
| ④ | From step 2 and step 3, this implies meet(a, a) equals a. Hence proven. | ④ | $meet(a, a) = a$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`Order · meet · meet with itself equals the argument`
