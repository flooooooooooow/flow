# examples.verify.math.derived

*Real addition associates.*

**Source.** landau — *Foundations of Analysis*

## Derived fact 1 — (x + y) + z = x + (y + z)

**Coordinate.** the real numbers · addition · parentheses do not matter · **Derived fact**

*Source: landau*

*Built on: zero is the left identity, for addition on the real numbers, zero is the right identity, for addition on the real numbers, order does not matter, for addition on the real numbers*

> **Goal.** (x + y) + z = x + (y + z)
>
> $$\forall x \in \mathbb{R} \forall y \in \mathbb{R} \forall z \in \mathbb{R}\quad (x + y) + z = x + (y + z)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that parentheses do not matter for addition on the real numbers. |  |  |
| ② | We invoke the definitional clause governing addition on the real numbers: zero is the left identity, for addition on the real numbers (instantiated for x + (y + z)). |  |  |
| ③ | We invoke the definitional clause governing addition on the real numbers: zero is the right identity, for addition on the real numbers (instantiated for (x + y) + z). |  |  |
| ④ | We invoke the derived fact governing addition on the real numbers: order does not matter, for addition on the real numbers (instantiated for x, y). |  |  |
| ⑤ | We invoke the derived fact governing addition on the real numbers: order does not matter, for addition on the real numbers (instantiated for y, z). |  |  |
| ⑥ | From step 2, step 3, step 4, and step 5, this implies (x plus y) plus z equals x plus (y plus z). Hence proven. | ⑥ | $(x + y) + z = x + (y + z)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ⑥ | step 2, step 3, step 4, and step 5 |

`the real numbers · addition · parentheses do not matter`
