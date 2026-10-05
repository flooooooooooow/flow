# examples.verify.math.derived

*Join is bounded below by its right argument.*

**Source.** davey-priestley — *Introduction to Lattices and Order*

## Derived fact 1 — b <= join(a, b)

**Coordinate.** Order · join · join is above the right argument · **Derived fact**

*Source: davey-priestley*

*Built on: order does not matter, for join on Order, join is above the left argument, for join on Order*

> **Goal.** b <= join(a, b)
>
> $$\forall a \in \mathbb{N} \forall b \in \mathbb{N}\quad b \le join(a, b)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that join is above the right argument for join on Order. |  |  |
| ② | We invoke the derived fact governing join on Order: order does not matter, for join on Order (instantiated for a, b). |  |  |
| ③ | We invoke the derived fact governing join on Order: join is above the left argument, for join on Order (instantiated for b, a). |  |  |
| ④ | From step 2 and step 3, this implies b is at most join(a, b). Hence proven. | ④ | $b \le join(a, b)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`Order · join · join is above the right argument`
