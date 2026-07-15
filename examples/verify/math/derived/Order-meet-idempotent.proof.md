# examples.verify.math.derived

*Meet is idempotent on the lattice order.*

**Source.** davey-priestley — *Introduction to Lattices and Order*

## Derived fact 1 — a ∧ a = a

**Coordinate.** Order · meet · repeating does not change the value · **Derived fact**

*Source: davey-priestley*

*Built on: order does not matter, for meet on Order*

> **Goal.** a ∧ a = a
>
> $$\forall a \in \mathbb{N}\quad meet(a, a) = a$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that repeating does not change the value for meet on Order. |  |  |
| ② | We invoke the derived fact governing meet on Order: order does not matter, for meet on Order (instantiated for a, a). |  |  |
| ③ | From step 2, this implies meet(a, a) equals a. Hence proven. | ③ | $meet(a, a) = a$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ③ | step 2 |

`Order · meet · repeating does not change the value`
