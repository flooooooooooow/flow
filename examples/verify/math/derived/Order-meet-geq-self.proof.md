# examples.verify.math.derived

*Meet is at most each argument.*

**Source.** davey-priestley — *Introduction to Lattices and Order*

## Derived fact 1 — meet(a, b) <= a

**Coordinate.** Order · meet · meet is at most the left argument · **Derived fact**

*Source: davey-priestley*

*Built on: meet is below the left argument, for meet on Order*

> **Goal.** meet(a, b) <= a
>
> $$\forall a \in \mathbb{N} \forall b \in \mathbb{N}\quad meet(a, b) \le a$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that meet is at most the left argument for meet on Order. |  |  |
| ② | We invoke the derived fact governing meet on Order: meet is below the left argument, for meet on Order (instantiated for a, b). |  |  |
| ③ | From step 2, this implies meet(a, b) is at most a. Hence proven. | ③ | $meet(a, b) \le a$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ③ | step 2 |

`Order · meet · meet is at most the left argument`
