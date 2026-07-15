# examples.verify.math.derived

*Zero times zero maps to zero under a group homomorphism.*

**Source.** dummit-foote — *Abstract Algebra*, §3.1

## Derived fact 1 — f(0 * 0) = 0

**Coordinate.** GroupHom · preservation · zero times zero maps to identity · **Derived fact**

*Source: dummit-foote*

*Built on: homomorphisms preserve multiplication, for preservation on GroupHom, homomorphisms preserve the identity, for preservation on GroupHom*

> **Goal.** f(0 * 0) = 0
>
> $$\forall f \in GroupHom\quad f(0^{2}) = 0$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that zero times zero maps to identity for preservation on GroupHom. |  |  |
| ② | We invoke the derived fact governing preservation on GroupHom: homomorphisms preserve multiplication, for preservation on GroupHom (instantiated for f, 0, 0). |  |  |
| ③ | We invoke the derived fact governing preservation on GroupHom: homomorphisms preserve the identity, for preservation on GroupHom (instantiated for f). |  |  |
| ④ | From step 2 and step 3, this implies f(0 times 0) equals 0. Hence proven. | ④ | $f(0^{2}) = 0$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`GroupHom · preservation · zero times zero maps to identity`
