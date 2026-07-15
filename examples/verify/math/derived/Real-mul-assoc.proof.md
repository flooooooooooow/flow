# examples.verify.math.derived

*Real multiplication associates.*

**Source.** landau — *Foundations of Analysis*

## Derived fact 1 — (x * y) * z = x * (y * z)

**Coordinate.** the real numbers · multiplication · parentheses do not matter · **Derived fact**

*Source: landau*

*Built on: one is the left identity, for multiplication on the real numbers, one is the right identity, for multiplication on the real numbers, order does not matter, for multiplication on the real numbers*

> **Goal.** (x * y) * z = x * (y * z)
>
> $$\forall x \in \mathbb{R} \forall y \in \mathbb{R} \forall z \in \mathbb{R}\quad (x \cdot y) * z = x * (y \cdot z)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that parentheses do not matter for multiplication on the real numbers. |  |  |
| ② | We invoke the definitional clause governing multiplication on the real numbers: one is the left identity, for multiplication on the real numbers (instantiated for x). |  |  |
| ③ | We invoke the derived fact governing multiplication on the real numbers: one is the right identity, for multiplication on the real numbers (instantiated for z). |  |  |
| ④ | We invoke the derived fact governing multiplication on the real numbers: order does not matter, for multiplication on the real numbers (instantiated for x, y). |  |  |
| ⑤ | We invoke the derived fact governing multiplication on the real numbers: order does not matter, for multiplication on the real numbers (instantiated for y, z). |  |  |
| ⑥ | From step 2, step 3, step 4, and step 5, this implies (x times y) times z equals x times (y times z). Hence proven. | ⑥ | $(x \cdot y) * z = x * (y \cdot z)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ⑥ | step 2, step 3, step 4, and step 5 |

`the real numbers · multiplication · parentheses do not matter`
