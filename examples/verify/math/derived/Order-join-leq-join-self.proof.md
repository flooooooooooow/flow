# examples.verify.math.derived

*Join of join with self is idempotent.*

**Source.** davey-priestley — *Introduction to Lattices and Order*

## Derived fact 1 — join(join(a, b), join(a, b)) = join(a, b)

**Coordinate.** Order · join · join of join with self is idempotent · **Derived fact**

*Source: davey-priestley*

*Built on: repeating does not change the value, for join on Order*

> **Goal.** join(join(a, b), join(a, b)) = join(a, b)
>
> $$\forall a \in \mathbb{N} \forall b \in \mathbb{N}\quad join(join(a, b), join(a, b)) = join(a, b)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that join of join with self is idempotent for join on Order. |  |  |
| ② | We invoke the derived fact governing join on Order: repeating does not change the value, for join on Order (instantiated for join(a, b)). |  |  |
| ③ | From step 2, this implies join(join(a, b), join(a, b)) equals join(a, b). Hence proven. | ③ | $join(join(a, b), join(a, b)) = join(a, b)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ③ | step 2 |

`Order · join · join of join with self is idempotent`
