# examples.verify.math.derived

*Join with itself returns the argument.*

**Source.** davey-priestley — *Introduction to Lattices and Order*

## Derived fact 1 — join(a, a) = a

**Coordinate.** Order · join · join with itself equals the argument · **Derived fact**

*Source: davey-priestley*

*Built on: repeating does not change the value, for join on Order, less-or-equal is reflexive, for order on the natural numbers*

> **Goal.** join(a, a) = a
>
> $$\forall a \in \mathbb{N}\quad join(a, a) = a$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that join with itself equals the argument for join on Order. |  |  |
| ② | We invoke the derived fact governing join on Order: repeating does not change the value, for join on Order (instantiated for a). |  |  |
| ③ | We invoke the derived fact governing order on the natural numbers: less-or-equal is reflexive, for order on the natural numbers (instantiated for a). |  |  |
| ④ | From step 2 and step 3, this implies join(a, a) equals a. Hence proven. | ④ | $join(a, a) = a$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`Order · join · join with itself equals the argument`
