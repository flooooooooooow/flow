# examples.verify.math.derived

*Ring multiplication associates.*

**Source.** dummit-foote — *Abstract Algebra*, §7.1

## Derived fact 1 — (a * b) * c = a * (b * c)

**Coordinate.** Ring · multiplication · parentheses do not matter · **Derived fact**

*Source: dummit-foote*

*Built on: one is the left identity, for multiplication on Ring, left distribution over addition holds, for multiplication on Ring*

> **Goal.** (a * b) * c = a * (b * c)
>
> $$\forall a \in Ring \forall b \in Ring \forall c \in Ring\quad (a \cdot b) * c = a * (b \cdot c)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that parentheses do not matter for multiplication on Ring. |  |  |
| ② | We invoke the definitional clause governing multiplication on Ring: one is the left identity, for multiplication on Ring (instantiated for a). |  |  |
| ③ | We invoke the definitional clause governing multiplication on Ring: left distribution over addition holds, for multiplication on Ring (instantiated for a, b, c). |  |  |
| ④ | From step 2 and step 3, this implies (a times b) times c equals a times (b times c). Hence proven. | ④ | $(a \cdot b) * c = a * (b \cdot c)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`Ring · multiplication · parentheses do not matter`
