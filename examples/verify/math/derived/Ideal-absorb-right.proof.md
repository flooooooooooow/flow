# examples.verify.math.derived

*Ideals absorb multiplication on the right.*

**Source.** dummit-foote — *Abstract Algebra*, §7.3

## Derived fact 1 — If a in I then a * r in I

**Coordinate.** Ideal · multiplication · absorbs ring elements on the right · **Derived fact**

*Source: dummit-foote*

*Built on: absorbs ring elements on the left, for multiplication on Ideal, one is the left identity, for multiplication on Ring*

> **Goal.** If a in I then a * r in I
>
> $$\forall I \in Ideal \forall r \in Ring \forall a \in Ring\quad a \cdot r in I$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that absorbs ring elements on the right for multiplication on Ideal. |  |  |
| ② | We split into exhaustive cases — the claim must hold in each one. |  |  |
| ③ | Case 1 (see step 2): suppose a in I. |  |  |
| ④ | We invoke the derived fact governing multiplication on Ideal: absorbs ring elements on the left, for multiplication on Ideal (instantiated for I, r, a). |  |  |
| ⑤ | We invoke the definitional clause governing multiplication on Ring: one is the left identity, for multiplication on Ring (instantiated for a). |  |  |
| ⑥ | From step 3, step 4, and step 5, this implies a times r in I. Together with the other cases (step 3), the goal is discharged. Hence proven. | ⑥ | $a \cdot r in I$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ③ | step 2 |
| ⑥ | step 3, step 4, and step 5 |

`Ideal · multiplication · absorbs ring elements on the right`
