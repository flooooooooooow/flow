# examples.verify.math.derived

*Inverses in a group are unique.*

**Source.** dummit-foote — *Abstract Algebra*, §1.1

## Derived fact 1 — If h * g = 1 and g * k = 1 then h = k

**Coordinate.** Group · inverse · inverses are unique · **Derived fact**

*Source: dummit-foote*

*Built on: left inverse recovers the identity, for inverse on Group, right inverse recovers the identity, for inverse on Group, parentheses do not matter, for multiplication on Group*

> **Goal.** If h * g = 1 and g * k = 1 then h = k
>
> $$\forall g \in Group \forall h \in Group \forall k \in Group\quad h = k$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that inverses are unique for inverse on Group. |  |  |
| ② | We split into exhaustive cases — the claim must hold in each one. |  |  |
| ③ | Case 1 (see step 2): suppose h * g  equals  1. |  |  |
| ④ | Case 2 (see step 2): suppose g * k  equals  1. |  |  |
| ⑤ | We invoke the definitional clause governing inverse on Group: left inverse recovers the identity, for inverse on Group (instantiated for g). |  |  |
| ⑥ | We invoke the derived fact governing inverse on Group: right inverse recovers the identity, for inverse on Group (instantiated for g). |  |  |
| ⑦ | We invoke the definitional clause governing multiplication on Group: parentheses do not matter, for multiplication on Group (instantiated for h, g, k). |  |  |
| ⑧ | From step 4, step 5, step 6, and step 7, this implies h equals k. Together with the other cases (step 3 and step 4), the goal is discharged. Hence proven. | ⑧ | $h = k$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ③ | step 2 |
| ④ | step 2 |
| ⑧ | step 4, step 5, step 6, and step 7 |

`Group · inverse · inverses are unique`
