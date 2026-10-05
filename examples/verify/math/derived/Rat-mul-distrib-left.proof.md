# examples.verify.math.derived

*Rational multiplication distributes over addition on the left.*

**Source.** landau — *Foundations of Analysis*

## Derived fact 1 — p * (q + r) = p * q + p * r

**Coordinate.** Rat · multiplication · left distribution over addition holds · **Derived fact**

*Source: landau*

*Built on: parentheses do not matter, for addition on Rat, parentheses do not matter, for multiplication on Rat, order does not matter, for multiplication on Rat*

> **Goal.** p * (q + r) = p * q + p * r
>
> $$\forall p \in Rat \forall q \in Rat \forall r \in Rat\quad p * (q + r) = p \cdot q + p \cdot r$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that left distribution over addition holds for multiplication on Rat. |  |  |
| ② | We invoke the derived fact governing addition on Rat: parentheses do not matter, for addition on Rat (instantiated for q, r, 0). |  |  |
| ③ | We invoke the derived fact governing multiplication on Rat: parentheses do not matter, for multiplication on Rat (instantiated for p, q, r). |  |  |
| ④ | We invoke the derived fact governing multiplication on Rat: order does not matter, for multiplication on Rat (instantiated for p, q). |  |  |
| ⑤ | From step 2, step 3, and step 4, this implies p times (q plus r) equals p times q plus p times r. Hence proven. | ⑤ | $p * (q + r) = p \cdot q + p \cdot r$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ⑤ | step 2, step 3, and step 4 |

`Rat · multiplication · left distribution over addition holds`
