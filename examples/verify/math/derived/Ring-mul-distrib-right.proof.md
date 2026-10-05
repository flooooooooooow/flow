# examples.verify.math.derived

*Ring multiplication distributes over addition on the right.*

**Source.** dummit-foote — *Abstract Algebra*, §7.1

## Derived fact 1 — (b + c) * a = b * a + c * a

**Coordinate.** Ring · multiplication · right distribution over addition holds · **Derived fact**

*Source: dummit-foote*

*Built on: left distribution over addition holds, for multiplication on Ring, order does not matter, for addition on Ring*

> **Goal.** (b + c) * a = b * a + c * a
>
> $$\forall a \in Ring \forall b \in Ring \forall c \in Ring\quad (b + c) * a = b \cdot a + c \cdot a$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that right distribution over addition holds for multiplication on Ring. |  |  |
| ② | We invoke the definitional clause governing multiplication on Ring: left distribution over addition holds, for multiplication on Ring (instantiated for a, b, c). |  |  |
| ③ | We invoke the definitional clause governing addition on Ring: order does not matter, for addition on Ring (instantiated for b, c). |  |  |
| ④ | From step 2 and step 3, this implies (b plus c) times a equals b times a plus c times a. Hence proven. | ④ | $(b + c) * a = b \cdot a + c \cdot a$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`Ring · multiplication · right distribution over addition holds`
