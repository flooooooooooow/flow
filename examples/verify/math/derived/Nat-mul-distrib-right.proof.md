# examples.verify.math.derived

*Multiplication distributes over addition on the left.*

**Source.** peano — https://en.wikipedia.org/wiki/Distributive_property

## Derived fact 1 — (a + b) * c = a * c + b * c

**Coordinate.** the natural numbers · multiplication · distributes over addition on the left · **Derived fact**

*Source: peano/induction — Gries & Schneider, Ch. 3*

*Built on: distributes over addition on the right, for multiplication on the natural numbers, order does not matter, for multiplication on the natural numbers*

> **Goal.** (a + b) * c = a * c + b * c
>
> $$\forall a \in \mathbb{N} \forall b \in \mathbb{N} \forall c \in \mathbb{N}\quad (a + b) * c = a \cdot c + b \cdot c$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that distributes over addition on the left for multiplication on the natural numbers. |  |  |
| ② | We invoke the derived fact governing multiplication on the natural numbers: distributes over addition on the right, for multiplication on the natural numbers (instantiated for c, a, b). |  |  |
| ③ | We invoke the derived fact governing multiplication on the natural numbers: order does not matter, for multiplication on the natural numbers (instantiated for a, c). |  |  |
| ④ | We invoke the derived fact governing multiplication on the natural numbers: order does not matter, for multiplication on the natural numbers (instantiated for b, c). |  |  |
| ⑤ | We invoke the derived fact governing multiplication on the natural numbers: order does not matter, for multiplication on the natural numbers (instantiated for a + b, c). |  |  |
| ⑥ | We invoke the derived fact governing multiplication on the natural numbers: order does not matter, for multiplication on the natural numbers (instantiated for c, a + b). |  |  |
| ⑦ | From step 2, step 3, step 4, step 5, and step 6, this implies (a plus b) times c equals a times c plus b times c. Hence proven. | ⑦ | $(a + b) * c = a \cdot c + b \cdot c$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ⑦ | step 2, step 3, step 4, step 5, and step 6 |

`the natural numbers · multiplication · distributes over addition on the left`
