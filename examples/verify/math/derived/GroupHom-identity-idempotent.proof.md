# examples.verify.math.derived

*The image of the identity is idempotent under a homomorphism.*

**Source.** dummit-foote — *Abstract Algebra*, §1.6

## Derived fact 1 — f(1) * f(1) = f(1)

**Coordinate.** GroupHom · identity · the identity image is idempotent · **Derived fact**

*Source: dummit-foote*

*Built on: products map to products, for multiplication on GroupHom, the identity maps to the identity, for identity on GroupHom*

> **Goal.** f(1) * f(1) = f(1)
>
> $$\forall f \in GroupHom\quad f(1) * f(1) = f(1)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that the identity image is idempotent for identity on GroupHom. |  |  |
| ② | We invoke the definitional clause governing multiplication on GroupHom: products map to products, for multiplication on GroupHom (instantiated for f, 1, 1). |  |  |
| ③ | We invoke the definitional clause governing identity on GroupHom: the identity maps to the identity, for identity on GroupHom (instantiated for f). |  |  |
| ④ | From step 2 and step 3, this implies f(1) times f(1) equals f(1). Hence proven. | ④ | $f(1) * f(1) = f(1)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`GroupHom · identity · the identity image is idempotent`
