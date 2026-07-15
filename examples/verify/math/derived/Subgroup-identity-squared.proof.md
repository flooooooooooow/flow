# examples.verify.math.derived

*The identity squared stays in a subgroup.*

**Source.** dummit-foote — *Abstract Algebra*, §2.2

## Derived fact 1 — If 1 in H then 1 * 1 in H

**Coordinate.** Subgroup · multiplication · identity squared stays in the subgroup · **Derived fact**

*Source: dummit-foote*

*Built on: subgroup products stay in the subgroup, for multiplication on Subgroup, subgroups contain the identity, for membership on Subgroup*

> **Goal.** If 1 in H then 1 * 1 in H
>
> $$\forall H \in Subgroup\quad 1^{2} in H$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that identity squared stays in the subgroup for multiplication on Subgroup. |  |  |
| ② | We split into exhaustive cases — the claim must hold in each one. |  |  |
| ③ | Case 1 (see step 2): suppose 1 in H. |  |  |
| ④ | We invoke the derived fact governing multiplication on Subgroup: subgroup products stay in the subgroup, for multiplication on Subgroup (instantiated for H, 1, 1). |  |  |
| ⑤ | We invoke the derived fact governing membership on Subgroup: subgroups contain the identity, for membership on Subgroup (instantiated for H). |  |  |
| ⑥ | From step 3, step 4, and step 5, this implies 1 times 1 in H. Together with the other cases (step 3), the goal is discharged. Hence proven. | ⑥ | $1^{2} in H$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ③ | step 2 |
| ⑥ | step 3, step 4, and step 5 |

`Subgroup · multiplication · identity squared stays in the subgroup`
