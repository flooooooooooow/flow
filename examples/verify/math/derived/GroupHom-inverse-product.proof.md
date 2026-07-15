# examples.verify.math.derived

*Homomorphisms send inverse products to one.*

**Source.** dummit-foote — *Abstract Algebra*, §1.6

## Derived fact 1 — f(g) * f(inv(g)) = 1

**Coordinate.** GroupHom · multiplication · products with inverses map to one · **Derived fact**

*Source: dummit-foote*

*Built on: products map to products, for multiplication on GroupHom, inverses map to inverses, for inverse on GroupHom, right inverse recovers the identity, for inverse on Group*

> **Goal.** f(g) * f(inv(g)) = 1
>
> $$\forall f \in GroupHom \forall g \in Group\quad f(g) * f(inv(g)) = 1$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that products with inverses map to one for multiplication on GroupHom. |  |  |
| ② | We invoke the definitional clause governing multiplication on GroupHom: products map to products, for multiplication on GroupHom (instantiated for f, g, inv(g)). |  |  |
| ③ | We invoke the derived fact governing inverse on GroupHom: inverses map to inverses, for inverse on GroupHom (instantiated for f, g). |  |  |
| ④ | We invoke the derived fact governing inverse on Group: right inverse recovers the identity, for inverse on Group (instantiated for g). |  |  |
| ⑤ | From step 2, step 3, and step 4, this implies f(g) times f(inv(g)) equals 1. Hence proven. | ⑤ | $f(g) * f(inv(g)) = 1$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ⑤ | step 2, step 3, and step 4 |

`GroupHom · multiplication · products with inverses map to one`
