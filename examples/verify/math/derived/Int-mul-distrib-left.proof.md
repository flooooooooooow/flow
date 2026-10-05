# examples.verify.math.derived

*Integer multiplication distributes over addition on the left.*

**Source.** landau — *Foundations of Analysis*, Ch. 1

## Derived fact 1 — a * (b + c) = a * b + a * c

**Coordinate.** the integers · multiplication · left distribution over addition holds · **Derived fact**

*Source: landau*

*Built on: parentheses do not matter, for addition on the integers, parentheses do not matter, for multiplication on the integers, negation distributes over addition, for negation on the integers*

> **Goal.** a * (b + c) = a * b + a * c
>
> $$\forall a \in \mathbb{Z} \forall b \in \mathbb{Z} \forall c \in \mathbb{Z}\quad a * (b + c) = a \cdot b + a \cdot c$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that left distribution over addition holds for multiplication on the integers. |  |  |
| ② | We invoke the derived fact governing addition on the integers: parentheses do not matter, for addition on the integers (instantiated for b, c, 0). |  |  |
| ③ | We invoke the derived fact governing multiplication on the integers: parentheses do not matter, for multiplication on the integers (instantiated for a, b, c). |  |  |
| ④ | We invoke the derived fact governing negation on the integers: negation distributes over addition, for negation on the integers (instantiated for b, c). |  |  |
| ⑤ | From step 2, step 3, and step 4, this implies a times (b plus c) equals a times b plus a times c. Hence proven. | ⑤ | $a * (b + c) = a \cdot b + a \cdot c$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ⑤ | step 2, step 3, and step 4 |

`the integers · multiplication · left distribution over addition holds`
