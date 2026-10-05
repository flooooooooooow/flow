# examples.verify.math.derived

*Join is idempotent on the lattice order.*

**Source.** davey-priestley — *Introduction to Lattices and Order*

## Derived fact 1 — a ∨ a = a

**Coordinate.** Order · join · repeating does not change the value · **Derived fact**

*Source: davey-priestley*

*Built on: order does not matter, for join on Order*

> **Goal.** a ∨ a = a
>
> $$\forall a \in \mathbb{N}\quad join(a, a) = a$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that repeating does not change the value for join on Order. |  |  |
| ② | We invoke the derived fact governing join on Order: order does not matter, for join on Order (instantiated for a, a). |  |  |
| ③ | From step 2, this implies join(a, a) equals a. Hence proven. | ③ | $join(a, a) = a$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ③ | step 2 |

`Order · join · repeating does not change the value`
