# examples.verify.math.derived

*Rational multiplication associates.*

**Source.** landau — *Foundations of Analysis*

## Derived fact 1 — (p * q) * r = p * (q * r)

**Coordinate.** Rat · multiplication · parentheses do not matter · **Derived fact**

*Source: landau*

*Built on: one is the left identity, for multiplication on Rat, one is the right identity, for multiplication on Rat, order does not matter, for multiplication on Rat*

> **Goal.** (p * q) * r = p * (q * r)
>
> $$\forall p \in Rat \forall q \in Rat \forall r \in Rat\quad (p \cdot q) * r = p * (q \cdot r)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that parentheses do not matter for multiplication on Rat. |  |  |
| ② | We invoke the definitional clause governing multiplication on Rat: one is the left identity, for multiplication on Rat (instantiated for p). |  |  |
| ③ | We invoke the derived fact governing multiplication on Rat: one is the right identity, for multiplication on Rat (instantiated for r). |  |  |
| ④ | We invoke the derived fact governing multiplication on Rat: order does not matter, for multiplication on Rat (instantiated for p, q). |  |  |
| ⑤ | We invoke the derived fact governing multiplication on Rat: order does not matter, for multiplication on Rat (instantiated for q, r). |  |  |
| ⑥ | From step 2, step 3, step 4, and step 5, this implies (p times q) times r equals p times (q times r). Hence proven. | ⑥ | $(p \cdot q) * r = p * (q \cdot r)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ⑥ | step 2, step 3, step 4, and step 5 |

`Rat · multiplication · parentheses do not matter`
