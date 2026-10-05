# examples.verify.math.derived

*Real multiplication distributes over addition on the left.*

**Source.** landau — *Foundations of Analysis*

## Derived fact 1 — x * (y + z) = x * y + x * z

**Coordinate.** the real numbers · multiplication · left distribution over addition holds · **Derived fact**

*Source: landau*

*Built on: parentheses do not matter, for addition on the real numbers, parentheses do not matter, for multiplication on the real numbers, zero is the right identity, for addition on the real numbers*

> **Goal.** x * (y + z) = x * y + x * z
>
> $$\forall x \in \mathbb{R} \forall y \in \mathbb{R} \forall z \in \mathbb{R}\quad x * (y + z) = x \cdot y + x \cdot z$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that left distribution over addition holds for multiplication on the real numbers. |  |  |
| ② | We invoke the derived fact governing addition on the real numbers: parentheses do not matter, for addition on the real numbers (instantiated for y, z, 0). |  |  |
| ③ | We invoke the derived fact governing multiplication on the real numbers: parentheses do not matter, for multiplication on the real numbers (instantiated for x, y, z). |  |  |
| ④ | We invoke the definitional clause governing addition on the real numbers: zero is the right identity, for addition on the real numbers (instantiated for x * y). |  |  |
| ⑤ | From step 2, step 3, and step 4, this implies x times (y plus z) equals x times y plus x times z. Hence proven. | ⑤ | $x * (y + z) = x \cdot y + x \cdot z$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ⑤ | step 2, step 3, and step 4 |

`the real numbers · multiplication · left distribution over addition holds`
