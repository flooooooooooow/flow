# examples.verify.math.derived

*Ring homomorphisms send zero to zero.*

**Source.** dummit-foote — *Abstract Algebra*, §7.3

## Derived fact 1 — f(0) = 0

**Coordinate.** RingHom · zero · zero maps to zero · **Derived fact**

*Source: dummit-foote*

*Built on: sums map to sums, for addition on RingHom, zero is the left identity, for addition on Ring*

> **Goal.** f(0) = 0
>
> $$\forall f \in RingHom\quad f(0) = 0$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that zero maps to zero for zero on RingHom. |  |  |
| ② | We invoke the definitional clause governing addition on RingHom: sums map to sums, for addition on RingHom (instantiated for f, 0, 0). |  |  |
| ③ | We invoke the definitional clause governing addition on Ring: zero is the left identity, for addition on Ring (instantiated for 0). |  |  |
| ④ | From step 2 and step 3, this implies f(0) equals 0. Hence proven. | ④ | $f(0) = 0$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`RingHom · zero · zero maps to zero`
