# examples.verify.math.derived

*Join is at least each argument.*

**Source.** davey-priestley — *Introduction to Lattices and Order*

## Derived fact 1 — a <= join(a, b)

**Coordinate.** Order · join · join is at least the left argument · **Derived fact**

*Source: davey-priestley*

*Built on: join is above the left argument, for join on Order*

> **Goal.** a <= join(a, b)
>
> $$\forall a \in \mathbb{N} \forall b \in \mathbb{N}\quad a \le join(a, b)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that join is at least the left argument for join on Order. |  |  |
| ② | We invoke the derived fact governing join on Order: join is above the left argument, for join on Order (instantiated for a, b). |  |  |
| ③ | From step 2, this implies a is at most join(a, b). Hence proven. | ③ | $a \le join(a, b)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ③ | step 2 |

`Order · join · join is at least the left argument`
