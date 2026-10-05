# examples.verify.math.derived

*One times one maps to one under a group homomorphism.*

**Source.** dummit-foote — *Abstract Algebra*, §3.1

## Derived fact 1 — f(1 * 1) = 1

**Coordinate.** GroupHom · preservation · one times one maps to identity · **Derived fact**

*Source: dummit-foote*

*Built on: homomorphisms preserve multiplication, for preservation on GroupHom, homomorphisms preserve the identity, for preservation on GroupHom*

> **Goal.** f(1 * 1) = 1
>
> $$\forall f \in GroupHom\quad f(1^{2}) = 1$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that one times one maps to identity for preservation on GroupHom. |  |  |
| ② | We invoke the derived fact governing preservation on GroupHom: homomorphisms preserve multiplication, for preservation on GroupHom (instantiated for f, 1, 1). |  |  |
| ③ | We invoke the derived fact governing preservation on GroupHom: homomorphisms preserve the identity, for preservation on GroupHom (instantiated for f). |  |  |
| ④ | From step 2 and step 3, this implies f(1 times 1) equals 1. Hence proven. | ④ | $f(1^{2}) = 1$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`GroupHom · preservation · one times one maps to identity`
