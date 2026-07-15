# examples.verify.math.derived

*Join absorbs meet on the lattice order.*

**Source.** davey-priestley — *Introduction to Lattices and Order*

## Derived fact 1 — a ∨ (a ∧ b) = a

**Coordinate.** Order · join · join absorbs meet · **Derived fact**

*Source: davey-priestley*

*Built on: order does not matter, for join on Order, order does not matter, for meet on Order, repeating does not change the value, for join on Order*

> **Goal.** a ∨ (a ∧ b) = a
>
> $$\forall a \in \mathbb{N} \forall b \in \mathbb{N}\quad join(a, meet(a, b)) = a$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that join absorbs meet for join on Order. |  |  |
| ② | We invoke the derived fact governing join on Order: order does not matter, for join on Order (instantiated for a, b). |  |  |
| ③ | We invoke the derived fact governing meet on Order: order does not matter, for meet on Order (instantiated for a, b). |  |  |
| ④ | We invoke the derived fact governing join on Order: repeating does not change the value, for join on Order (instantiated for a). |  |  |
| ⑤ | From step 2, step 3, and step 4, this implies join(a, meet(a, b)) equals a. Hence proven. | ⑤ | $join(a, meet(a, b)) = a$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ⑤ | step 2, step 3, and step 4 |

`Order · join · join absorbs meet`
