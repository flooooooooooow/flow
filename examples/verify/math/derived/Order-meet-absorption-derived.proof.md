# examples.verify.math.derived

*Meet absorbs join as a derived lattice law.*

**Source.** davey-priestley — *Introduction to Lattices and Order*

## Derived fact 1 — meet(a, join(a, b)) = a

**Coordinate.** Order · meet · meet absorbs join derived · **Derived fact**

*Source: davey-priestley*

*Built on: meet absorbs join, for meet on Order*

> **Goal.** meet(a, join(a, b)) = a
>
> $$\forall a \in \mathbb{N} \forall b \in \mathbb{N}\quad meet(a, join(a, b)) = a$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that meet absorbs join derived for meet on Order. |  |  |
| ② | We invoke the derived fact governing meet on Order: meet absorbs join, for meet on Order (instantiated for a, b). |  |  |
| ③ | From step 2, this implies meet(a, join(a, b)) equals a. Hence proven. | ③ | $meet(a, join(a, b)) = a$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ③ | step 2 |

`Order · meet · meet absorbs join derived`
