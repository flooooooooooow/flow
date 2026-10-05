# examples.verify.math.derived

*Integer addition associates.*

**Source.** landau — *Foundations of Analysis*, Ch. 1

## Derived fact 1 — (a + b) + c = a + (b + c)

**Coordinate.** the integers · addition · parentheses do not matter · **Derived fact**

*Source: landau*

*Built on: zero is the left identity, for addition on the integers, zero is the right identity, for addition on the integers, order does not matter, for addition on the integers*

> **Goal.** (a + b) + c = a + (b + c)
>
> $$\forall a \in \mathbb{Z} \forall b \in \mathbb{Z} \forall c \in \mathbb{Z}\quad (a + b) + c = a + (b + c)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that parentheses do not matter for addition on the integers. |  |  |
| ② | We invoke the definitional clause governing addition on the integers: zero is the left identity, for addition on the integers (instantiated for a + (b + c)). |  |  |
| ③ | We invoke the definitional clause governing addition on the integers: zero is the right identity, for addition on the integers (instantiated for (a + b) + c). |  |  |
| ④ | We invoke the derived fact governing addition on the integers: order does not matter, for addition on the integers (instantiated for a, b). |  |  |
| ⑤ | We invoke the derived fact governing addition on the integers: order does not matter, for addition on the integers (instantiated for b, c). |  |  |
| ⑥ | From step 2, step 3, step 4, and step 5, this implies (a plus b) plus c equals a plus (b plus c). Hence proven. | ⑥ | $(a + b) + c = a + (b + c)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ⑥ | step 2, step 3, step 4, and step 5 |

`the integers · addition · parentheses do not matter`
