# examples.verify.math.derived

*Integer multiplication distributes over addition on the right.*

**Source.** landau — *Foundations of Analysis*, Ch. 1

## Derived fact 1 — (b + c) * a = b * a + c * a

**Coordinate.** the integers · multiplication · right distribution over addition holds · **Derived fact**

*Source: landau*

*Built on: left distribution over addition holds, for multiplication on the integers, order does not matter, for multiplication on the integers*

> **Goal.** (b + c) * a = b * a + c * a
>
> $$\forall a \in \mathbb{Z} \forall b \in \mathbb{Z} \forall c \in \mathbb{Z}\quad (b + c) * a = b \cdot a + c \cdot a$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that right distribution over addition holds for multiplication on the integers. |  |  |
| ② | We invoke the derived fact governing multiplication on the integers: left distribution over addition holds, for multiplication on the integers (instantiated for a, b, c). |  |  |
| ③ | We invoke the derived fact governing multiplication on the integers: order does not matter, for multiplication on the integers (instantiated for b, a). |  |  |
| ④ | We invoke the derived fact governing multiplication on the integers: order does not matter, for multiplication on the integers (instantiated for c, a). |  |  |
| ⑤ | From step 2, step 3, and step 4, this implies (b plus c) times a equals b times a plus c times a. Hence proven. | ⑤ | $(b + c) * a = b \cdot a + c \cdot a$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ⑤ | step 2, step 3, and step 4 |

`the integers · multiplication · right distribution over addition holds`
