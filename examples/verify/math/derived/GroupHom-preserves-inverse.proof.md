# examples.verify.math.derived

*Group homomorphisms preserve inverses.*

**Source.** dummit-foote — *Abstract Algebra*, §1.6

## Derived fact 1 — f(inv(g)) = inv(f(g))

**Coordinate.** GroupHom · inverse · inverses map to inverses · **Derived fact**

*Source: dummit-foote*

*Built on: the identity maps to the identity, for identity on GroupHom, products map to products, for multiplication on GroupHom, right inverse recovers the identity, for inverse on Group*

> **Goal.** f(inv(g)) = inv(f(g))
>
> $$\forall f \in GroupHom \forall g \in Group\quad f(inv(g)) = inv(f(g))$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that inverses map to inverses for inverse on GroupHom. |  |  |
| ② | We invoke the definitional clause governing identity on GroupHom: the identity maps to the identity, for identity on GroupHom (instantiated for f). |  |  |
| ③ | We invoke the definitional clause governing multiplication on GroupHom: products map to products, for multiplication on GroupHom (instantiated for f, g, inv(g)). |  |  |
| ④ | We invoke the derived fact governing inverse on Group: right inverse recovers the identity, for inverse on Group (instantiated for g). |  |  |
| ⑤ | From step 2, step 3, and step 4, this implies f(inv(g)) equals inv(f(g)). Hence proven. | ⑤ | $f(inv(g)) = inv(f(g))$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ⑤ | step 2, step 3, and step 4 |

`GroupHom · inverse · inverses map to inverses`
