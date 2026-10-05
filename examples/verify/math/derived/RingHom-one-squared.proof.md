# examples.verify.math.derived

*A ring homomorphism squares the unity.*

**Source.** dummit-foote — *Abstract Algebra*, §7.3

## Derived fact 1 — f(1) * f(1) = 1

**Coordinate.** RingHom · multiplication · one squared maps to one · **Derived fact**

*Source: dummit-foote*

*Built on: products map to products, for multiplication on RingHom, one maps to one, for multiplication on RingHom*

> **Goal.** f(1) * f(1) = 1
>
> $$\forall f \in RingHom\quad f(1) * f(1) = 1$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that one squared maps to one for multiplication on RingHom. |  |  |
| ② | We invoke the definitional clause governing multiplication on RingHom: products map to products, for multiplication on RingHom (instantiated for f, 1, 1). |  |  |
| ③ | We invoke the derived fact governing multiplication on RingHom: one maps to one, for multiplication on RingHom (instantiated for f). |  |  |
| ④ | From step 2 and step 3, this implies f(1) times f(1) equals 1. Hence proven. | ④ | $f(1) * f(1) = 1$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`RingHom · multiplication · one squared maps to one`
