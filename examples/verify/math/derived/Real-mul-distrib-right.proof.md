# examples.verify.math.derived

*Real multiplication distributes over addition on the right.*

**Source.** landau — *Foundations of Analysis*

## Derived fact 1 — (y + z) * x = y * x + z * x

**Coordinate.** the real numbers · multiplication · right distribution over addition holds · **Derived fact**

*Source: landau*

*Built on: left distribution over addition holds, for multiplication on the real numbers, order does not matter, for multiplication on the real numbers*

> **Goal.** (y + z) * x = y * x + z * x
>
> $$\forall x \in \mathbb{R} \forall y \in \mathbb{R} \forall z \in \mathbb{R}\quad (y + z) * x = y \cdot x + z \cdot x$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that right distribution over addition holds for multiplication on the real numbers. |  |  |
| ② | We invoke the derived fact governing multiplication on the real numbers: left distribution over addition holds, for multiplication on the real numbers (instantiated for x, y, z). |  |  |
| ③ | We invoke the derived fact governing multiplication on the real numbers: order does not matter, for multiplication on the real numbers (instantiated for y, x). |  |  |
| ④ | We invoke the derived fact governing multiplication on the real numbers: order does not matter, for multiplication on the real numbers (instantiated for z, x). |  |  |
| ⑤ | From step 2, step 3, and step 4, this implies (y plus z) times x equals y times x plus z times x. Hence proven. | ⑤ | $(y + z) * x = y \cdot x + z \cdot x$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ⑤ | step 2, step 3, and step 4 |

`the real numbers · multiplication · right distribution over addition holds`
