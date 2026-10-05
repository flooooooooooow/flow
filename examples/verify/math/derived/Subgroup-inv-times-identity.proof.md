# examples.verify.math.derived

*The inverse of the identity times the identity stays in a subgroup.*

**Source.** dummit-foote — *Abstract Algebra*, §2.2

## Derived fact 1 — inv(1) * 1 in H for every subgroup H

**Coordinate.** Subgroup · multiplication · identity inverse times identity stays in the subgroup · **Derived fact**

*Source: dummit-foote*

*Built on: subgroup products stay in the subgroup, for multiplication on Subgroup, identity inverse stays in the subgroup, for inverse on Subgroup, subgroups contain the identity, for membership on Subgroup*

> **Goal.** inv(1) * 1 in H for every subgroup H
>
> $$\forall H \in Subgroup\quad inv(1) * 1 in H$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that identity inverse times identity stays in the subgroup for multiplication on Subgroup. |  |  |
| ② | We split into exhaustive cases — the claim must hold in each one. |  |  |
| ③ | Case 1 (see step 2): suppose 1 in H. |  |  |
| ④ | Case 2 (see step 2): suppose inv(1) in H. |  |  |
| ⑤ | We invoke the derived fact governing multiplication on Subgroup: subgroup products stay in the subgroup, for multiplication on Subgroup (instantiated for H, inv(1), 1). |  |  |
| ⑥ | We invoke the derived fact governing inverse on Subgroup: identity inverse stays in the subgroup, for inverse on Subgroup (instantiated for H). |  |  |
| ⑦ | We invoke the derived fact governing membership on Subgroup: subgroups contain the identity, for membership on Subgroup (instantiated for H). |  |  |
| ⑧ | From step 4, step 5, step 6, and step 7, this implies inv(1) times 1 in H. Together with the other cases (step 3 and step 4), the goal is discharged. Hence proven. | ⑧ | $inv(1) * 1 in H$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ③ | step 2 |
| ④ | step 2 |
| ⑧ | step 4, step 5, step 6, and step 7 |

`Subgroup · multiplication · identity inverse times identity stays in the subgroup`
