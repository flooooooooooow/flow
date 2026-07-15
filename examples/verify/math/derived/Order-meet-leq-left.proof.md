# examples.verify.math.derived

*Meet is bounded above by its left argument.*

**Source.** davey-priestley — *Introduction to Lattices and Order*

## Derived fact 1 — meet(a, b) <= a

**Coordinate.** Order · meet · meet is below the left argument · **Derived fact**

*Source: davey-priestley*

*Built on: meet absorbs join, for meet on Order, less-or-equal is reflexive, for order on the natural numbers*

> **Goal.** meet(a, b) <= a
>
> $$\forall a \in \mathbb{N} \forall b \in \mathbb{N}\quad meet(a, b) \le a$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that meet is below the left argument for meet on Order. |  |  |
| ② | We invoke the derived fact governing meet on Order: meet absorbs join, for meet on Order (instantiated for a, b). |  |  |
| ③ | We invoke the derived fact governing order on the natural numbers: less-or-equal is reflexive, for order on the natural numbers (instantiated for meet(a, b)). |  |  |
| ④ | From step 2 and step 3, this implies meet(a, b) is at most a. Hence proven. | ④ | $meet(a, b) \le a$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`Order · meet · meet is below the left argument`
