# examples.verify.math.derived

*Left and right inverses coincide in a group.*

**Source.** dummit-foote — *Abstract Algebra*, §1.1

## Derived fact 1 — If h * g = 1 and g * inv(g) = 1 then h = inv(g)

**Coordinate.** Group · inverse · left and right inverses agree · **Derived fact**

*Source: dummit-foote*

*Built on: inverses are unique, for inverse on Group, right inverse recovers the identity, for inverse on Group*

> **Goal.** If h * g = 1 and g * inv(g) = 1 then h = inv(g)
>
> $$\forall g \in Group \forall h \in Group\quad h = inv(g)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that left and right inverses agree for inverse on Group. |  |  |
| ② | We split into exhaustive cases — the claim must hold in each one. |  |  |
| ③ | Case 1 (see step 2): suppose h * g  equals  1. |  |  |
| ④ | Case 2 (see step 2): suppose g * inv(g)  equals  1. |  |  |
| ⑤ | We invoke the derived fact governing inverse on Group: inverses are unique, for inverse on Group (instantiated for g, h, inv(g)). |  |  |
| ⑥ | We invoke the derived fact governing inverse on Group: right inverse recovers the identity, for inverse on Group (instantiated for g). |  |  |
| ⑦ | From step 4, step 5, and step 6, this implies h equals inv(g). Together with the other cases (step 3 and step 4), the goal is discharged. Hence proven. | ⑦ | $h = inv(g)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ③ | step 2 |
| ④ | step 2 |
| ⑦ | step 4, step 5, and step 6 |

`Group · inverse · left and right inverses agree`
