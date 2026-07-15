# examples.verify.math.derived

*Integer multiplication associates.*

**Source.** landau — *Foundations of Analysis*, Ch. 1

## Derived fact 1 — (a * b) * c = a * (b * c)

**Coordinate.** the integers · multiplication · parentheses do not matter · **Derived fact**

*Source: landau*

*Built on: one is the left identity, for multiplication on the integers, one is the right identity, for multiplication on the integers, order does not matter, for multiplication on the integers*

> **Goal.** (a * b) * c = a * (b * c)
>
> $$\forall a \in \mathbb{Z} \forall b \in \mathbb{Z} \forall c \in \mathbb{Z}\quad (a \cdot b) * c = a * (b \cdot c)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that parentheses do not matter for multiplication on the integers. |  |  |
| ② | We invoke the derived fact governing multiplication on the integers: one is the left identity, for multiplication on the integers (instantiated for a). |  |  |
| ③ | We invoke the derived fact governing multiplication on the integers: one is the right identity, for multiplication on the integers (instantiated for c). |  |  |
| ④ | We invoke the derived fact governing multiplication on the integers: order does not matter, for multiplication on the integers (instantiated for a, b). |  |  |
| ⑤ | We invoke the derived fact governing multiplication on the integers: order does not matter, for multiplication on the integers (instantiated for b, c). |  |  |
| ⑥ | From step 2, step 3, step 4, and step 5, this implies (a times b) times c equals a times (b times c). Hence proven. | ⑥ | $(a \cdot b) * c = a * (b \cdot c)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ⑥ | step 2, step 3, step 4, and step 5 |

`the integers · multiplication · parentheses do not matter`
