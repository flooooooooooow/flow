# examples.verify.math.derived

*A ring homomorphism sends one times zero to zero.*

**Source.** dummit-foote — *Abstract Algebra*, §7.3

## Derived fact 1 — f(1) * 0 = 0

**Coordinate.** RingHom · multiplication · one times zero maps to zero · **Derived fact**

*Source: dummit-foote*

*Built on: one maps to one, for multiplication on RingHom, one times zero is zero, for multiplication on Ring*

> **Goal.** f(1) * 0 = 0
>
> $$\forall f \in RingHom\quad f(1) * 0 = 0$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that one times zero maps to zero for multiplication on RingHom. |  |  |
| ② | We invoke the derived fact governing multiplication on RingHom: one maps to one, for multiplication on RingHom (instantiated for f). |  |  |
| ③ | We invoke the derived fact governing multiplication on Ring: one times zero is zero, for multiplication on Ring. |  |  |
| ④ | From step 2 and step 3, this implies f(1) times 0 equals 0. Hence proven. | ④ | $f(1) * 0 = 0$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`RingHom · multiplication · one times zero maps to zero`
