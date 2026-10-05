# examples.verify.math.derived

*Join is bounded below by its left argument.*

**Source.** davey-priestley — *Introduction to Lattices and Order*

## Derived fact 1 — a <= join(a, b)

**Coordinate.** Order · join · join is above the left argument · **Derived fact**

*Source: davey-priestley*

*Built on: join absorbs meet, for join on Order, meet is below join, for lattice on Order*

> **Goal.** a <= join(a, b)
>
> $$\forall a \in \mathbb{N} \forall b \in \mathbb{N}\quad a \le join(a, b)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that join is above the left argument for join on Order. |  |  |
| ② | We invoke the derived fact governing join on Order: join absorbs meet, for join on Order (instantiated for a, b). |  |  |
| ③ | We invoke the derived fact governing lattice on Order: meet is below join, for lattice on Order (instantiated for a, b). |  |  |
| ④ | From step 2 and step 3, this implies a is at most join(a, b). Hence proven. | ④ | $a \le join(a, b)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`Order · join · join is above the left argument`
