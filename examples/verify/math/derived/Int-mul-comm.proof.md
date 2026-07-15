# examples.verify.math.derived

*Integer multiplication commutes.*

**Source.** landau — *Foundations of Analysis*, Ch. 1

## Derived fact 1 — a * b = b * a

**Coordinate.** the integers · multiplication · order does not matter · **Derived fact**

*Source: landau*

*Built on: one is the right identity, for multiplication on the integers, order does not matter, for addition on the integers*

> **Goal.** a * b = b * a
>
> $$\forall a \in \mathbb{Z} \forall b \in \mathbb{Z}\quad a \cdot b = b \cdot a$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that order does not matter for multiplication on the integers. |  |  |
| ② | We invoke the derived fact governing multiplication on the integers: one is the right identity, for multiplication on the integers (instantiated for a). |  |  |
| ③ | We invoke the derived fact governing multiplication on the integers: one is the right identity, for multiplication on the integers (instantiated for b). |  |  |
| ④ | We invoke the derived fact governing addition on the integers: order does not matter, for addition on the integers (instantiated for a, b). |  |  |
| ⑤ | From step 2, step 3, and step 4, this implies a times b equals b times a. Hence proven. | ⑤ | $a \cdot b = b \cdot a$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ⑤ | step 2, step 3, and step 4 |

`the integers · multiplication · order does not matter`
