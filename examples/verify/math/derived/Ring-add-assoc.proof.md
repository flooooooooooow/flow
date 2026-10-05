# examples.verify.math.derived

*Ring addition associates.*

**Source.** dummit-foote — *Abstract Algebra*, §7.1

## Derived fact 1 — (a + b) + c = a + (b + c)

**Coordinate.** Ring · addition · parentheses do not matter · **Derived fact**

*Source: dummit-foote*

*Built on: order does not matter, for addition on Ring, zero is the left identity, for addition on Ring*

> **Goal.** (a + b) + c = a + (b + c)
>
> $$\forall a \in Ring \forall b \in Ring \forall c \in Ring\quad (a + b) + c = a + (b + c)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that parentheses do not matter for addition on Ring. |  |  |
| ② | We invoke the definitional clause governing addition on Ring: order does not matter, for addition on Ring (instantiated for a, b). |  |  |
| ③ | We invoke the definitional clause governing addition on Ring: order does not matter, for addition on Ring (instantiated for b, c). |  |  |
| ④ | We invoke the definitional clause governing addition on Ring: zero is the left identity, for addition on Ring (instantiated for a + (b + c)). |  |  |
| ⑤ | From step 2, step 3, and step 4, this implies (a plus b) plus c equals a plus (b plus c). Hence proven. | ⑤ | $(a + b) + c = a + (b + c)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ⑤ | step 2, step 3, and step 4 |

`Ring · addition · parentheses do not matter`
