# examples.verify.math.derived

*Join with itself is above the argument.*

**Source.** davey-priestley — *Introduction to Lattices and Order*

## Derived fact 1 — a <= join(a, a)

**Coordinate.** Order · join · join with itself is above the argument · **Derived fact**

*Source: davey-priestley*

*Built on: repeating does not change the value, for join on Order, join is above the left argument, for join on Order*

> **Goal.** a <= join(a, a)
>
> $$\forall a \in \mathbb{N}\quad a \le join(a, a)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that join with itself is above the argument for join on Order. |  |  |
| ② | We invoke the derived fact governing join on Order: repeating does not change the value, for join on Order (instantiated for a). |  |  |
| ③ | We invoke the derived fact governing join on Order: join is above the left argument, for join on Order (instantiated for a, a). |  |  |
| ④ | From step 2 and step 3, this implies a is at most join(a, a). Hence proven. | ④ | $a \le join(a, a)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`Order · join · join with itself is above the argument`
