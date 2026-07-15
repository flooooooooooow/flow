# examples.verify.math.derived

*Real multiplication commutes.*

**Source.** landau — *Foundations of Analysis*

## Derived fact 1 — x * y = y * x

**Coordinate.** the real numbers · multiplication · order does not matter · **Derived fact**

*Source: landau*

*Built on: one is the left identity, for multiplication on the real numbers, one is the right identity, for multiplication on the real numbers, order does not matter, for addition on the real numbers*

> **Goal.** x * y = y * x
>
> $$\forall x \in \mathbb{R} \forall y \in \mathbb{R}\quad x \cdot y = y \cdot x$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that order does not matter for multiplication on the real numbers. |  |  |
| ② | We invoke the definitional clause governing multiplication on the real numbers: one is the left identity, for multiplication on the real numbers (instantiated for x). |  |  |
| ③ | We invoke the derived fact governing multiplication on the real numbers: one is the right identity, for multiplication on the real numbers (instantiated for y). |  |  |
| ④ | We invoke the derived fact governing addition on the real numbers: order does not matter, for addition on the real numbers (instantiated for x, y). |  |  |
| ⑤ | From step 2, step 3, and step 4, this implies x times y equals y times x. Hence proven. | ⑤ | $x \cdot y = y \cdot x$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ⑤ | step 2, step 3, and step 4 |

`the real numbers · multiplication · order does not matter`
