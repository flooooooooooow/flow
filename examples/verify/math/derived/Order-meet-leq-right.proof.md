# examples.verify.math.derived

*Meet is bounded above by its right argument.*

**Source.** davey-priestley — *Introduction to Lattices and Order*

## Derived fact 1 — meet(a, b) <= b

**Coordinate.** Order · meet · meet is below the right argument · **Derived fact**

*Source: davey-priestley*

*Built on: order does not matter, for meet on Order, meet is below the left argument, for meet on Order*

> **Goal.** meet(a, b) <= b
>
> $$\forall a \in \mathbb{N} \forall b \in \mathbb{N}\quad meet(a, b) \le b$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that meet is below the right argument for meet on Order. |  |  |
| ② | We invoke the derived fact governing meet on Order: order does not matter, for meet on Order (instantiated for a, b). |  |  |
| ③ | We invoke the derived fact governing meet on Order: meet is below the left argument, for meet on Order (instantiated for b, a). |  |  |
| ④ | From step 2 and step 3, this implies meet(a, b) is at most b. Hence proven. | ④ | $meet(a, b) \le b$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`Order · meet · meet is below the right argument`
