# examples.verify.math.derived

*Right cancellation holds in a group.*

**Source.** dummit-foote — *Abstract Algebra*, §1.1

## Derived fact 1 — b * a = c * a implies b = c

**Coordinate.** Group · multiplication · right cancellation holds · **Derived fact**

*Source: dummit-foote*

*Built on: left inverse recovers the identity, for inverse on Group, parentheses do not matter, for multiplication on Group, one is the right identity, for identity on Group*

> **Goal.** b * a = c * a implies b = c
>
> $$\forall a \in Group \forall b \in Group \forall c \in Group\quad b = c$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that right cancellation holds for multiplication on Group. |  |  |
| ② | We split into exhaustive cases — the claim must hold in each one. |  |  |
| ③ | Case 1 (see step 2): suppose b * a  equals  c * a. |  |  |
| ④ | We invoke the definitional clause governing inverse on Group: left inverse recovers the identity, for inverse on Group (instantiated for a). |  |  |
| ⑤ | We invoke the definitional clause governing multiplication on Group: parentheses do not matter, for multiplication on Group (instantiated for b, a, inv(a)). |  |  |
| ⑥ | We invoke the definitional clause governing identity on Group: one is the right identity, for identity on Group (instantiated for b). |  |  |
| ⑦ | From step 3, step 4, step 5, and step 6, this implies b equals c. Together with the other cases (step 3), the goal is discharged. Hence proven. | ⑦ | $b = c$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ③ | step 2 |
| ⑦ | step 3, step 4, step 5, and step 6 |

`Group · multiplication · right cancellation holds`
