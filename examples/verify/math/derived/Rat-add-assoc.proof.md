# examples.verify.math.derived

*Rational addition associates.*

**Source.** landau — *Foundations of Analysis*

## Derived fact 1 — (p + q) + r = p + (q + r)

**Coordinate.** Rat · addition · parentheses do not matter · **Derived fact**

*Source: landau*

*Built on: zero is the left identity, for addition on Rat, zero is the right identity, for addition on Rat, order does not matter, for addition on Rat*

> **Goal.** (p + q) + r = p + (q + r)
>
> $$\forall p \in Rat \forall q \in Rat \forall r \in Rat\quad (p + q) + r = p + (q + r)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that parentheses do not matter for addition on Rat. |  |  |
| ② | We invoke the definitional clause governing addition on Rat: zero is the left identity, for addition on Rat (instantiated for p + (q + r)). |  |  |
| ③ | We invoke the definitional clause governing addition on Rat: zero is the right identity, for addition on Rat (instantiated for (p + q) + r). |  |  |
| ④ | We invoke the derived fact governing addition on Rat: order does not matter, for addition on Rat (instantiated for p, q). |  |  |
| ⑤ | We invoke the derived fact governing addition on Rat: order does not matter, for addition on Rat (instantiated for q, r). |  |  |
| ⑥ | From step 2, step 3, step 4, and step 5, this implies (p plus q) plus r equals p plus (q plus r). Hence proven. | ⑥ | $(p + q) + r = p + (q + r)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ⑥ | step 2, step 3, step 4, and step 5 |

`Rat · addition · parentheses do not matter`
