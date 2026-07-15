# examples.verify.math.derived

*A ring homomorphism sends zero times one to zero.*

**Source.** dummit-foote — *Abstract Algebra*, §7.3

## Derived fact 1 — f(0) * 1 = 0

**Coordinate.** RingHom · multiplication · zero times one maps to zero · **Derived fact**

*Source: dummit-foote*

*Built on: zero maps to zero, for zero on RingHom, zero on the left gives zero, for multiplication on Ring*

> **Goal.** f(0) * 1 = 0
>
> $$\forall f \in RingHom\quad f(0) * 1 = 0$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that zero times one maps to zero for multiplication on RingHom. |  |  |
| ② | We invoke the derived fact governing zero on RingHom: zero maps to zero, for zero on RingHom (instantiated for f). |  |  |
| ③ | We invoke the derived fact governing multiplication on Ring: zero on the left gives zero, for multiplication on Ring (instantiated for 1). |  |  |
| ④ | From step 2 and step 3, this implies f(0) times 1 equals 0. Hence proven. | ④ | $f(0) * 1 = 0$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`RingHom · multiplication · zero times one maps to zero`
