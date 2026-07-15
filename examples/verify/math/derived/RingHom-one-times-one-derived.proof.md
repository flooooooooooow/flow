# examples.verify.math.derived

*One times one maps to one under a ring homomorphism.*

**Source.** dummit-foote — *Abstract Algebra*, §7.3

## Derived fact 1 — f(1 * 1) = 1

**Coordinate.** RingHom · preservation · one times one maps to one derived · **Derived fact**

*Source: dummit-foote*

*Built on: homomorphisms preserve multiplication, for preservation on RingHom, homomorphisms preserve one, for preservation on RingHom*

> **Goal.** f(1 * 1) = 1
>
> $$\forall f \in RingHom\quad f(1^{2}) = 1$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that one times one maps to one derived for preservation on RingHom. |  |  |
| ② | We invoke the derived fact governing preservation on RingHom: homomorphisms preserve multiplication, for preservation on RingHom (instantiated for f, 1, 1). |  |  |
| ③ | We invoke the derived fact governing preservation on RingHom: homomorphisms preserve one, for preservation on RingHom (instantiated for f). |  |  |
| ④ | From step 2 and step 3, this implies f(1 times 1) equals 1. Hence proven. | ④ | $f(1^{2}) = 1$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`RingHom · preservation · one times one maps to one derived`
