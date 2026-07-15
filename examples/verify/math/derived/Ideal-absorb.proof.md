# examples.verify.math.derived

*Ideals absorb multiplication by ring elements.*

**Source.** dummit-foote — *Abstract Algebra*, §7.3

## Derived fact 1 — If a in I and r in R then r * a in I

**Coordinate.** Ideal · multiplication · absorbs ring elements on the left · **Derived fact**

*Source: dummit-foote*

*Built on: zero lies in every ideal, for membership on Ideal, left distribution over addition holds, for multiplication on Ring*

> **Goal.** If a in I and r in R then r * a in I
>
> $$\forall I \in Ideal \forall r \in Ring \forall a \in Ring\quad r \cdot a in I$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that absorbs ring elements on the left for multiplication on Ideal. |  |  |
| ② | We split into exhaustive cases — the claim must hold in each one. |  |  |
| ③ | Case 1 (see step 2): suppose a in I. |  |  |
| ④ | We invoke the definitional clause governing membership on Ideal: zero lies in every ideal, for membership on Ideal (instantiated for I). |  |  |
| ⑤ | We invoke the definitional clause governing multiplication on Ring: left distribution over addition holds, for multiplication on Ring (instantiated for r, a, 0). |  |  |
| ⑥ | From step 3, step 4, and step 5, this implies r times a in I. Together with the other cases (step 3), the goal is discharged. Hence proven. | ⑥ | $r \cdot a in I$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ③ | step 2 |
| ⑥ | step 3, step 4, and step 5 |

`Ideal · multiplication · absorbs ring elements on the left`
