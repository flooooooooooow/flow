# examples.verify.math.derived

*Multiplying zero by a ring element stays in an ideal.*

**Source.** dummit-foote — *Abstract Algebra*, §7.3

## Derived fact 1 — If 0 in I then r * 0 in I

**Coordinate.** Ideal · multiplication · zero product stays in the ideal · **Derived fact**

*Source: dummit-foote*

*Built on: absorbs ring elements on the left, for multiplication on Ideal, ideals contain zero, for membership on Ideal*

> **Goal.** If 0 in I then r * 0 in I
>
> $$\forall I \in Ideal \forall r \in Ring\quad r \cdot 0 in I$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that zero product stays in the ideal for multiplication on Ideal. |  |  |
| ② | We split into exhaustive cases — the claim must hold in each one. |  |  |
| ③ | Case 1 (see step 2): suppose 0 in I. |  |  |
| ④ | We invoke the derived fact governing multiplication on Ideal: absorbs ring elements on the left, for multiplication on Ideal (instantiated for I, r, 0). |  |  |
| ⑤ | We invoke the derived fact governing membership on Ideal: ideals contain zero, for membership on Ideal (instantiated for I). |  |  |
| ⑥ | From step 3, step 4, and step 5, this implies r times 0 in I. Together with the other cases (step 3), the goal is discharged. Hence proven. | ⑥ | $r \cdot 0 in I$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ③ | step 2 |
| ⑥ | step 3, step 4, and step 5 |

`Ideal · multiplication · zero product stays in the ideal`
