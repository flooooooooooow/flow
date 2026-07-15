# examples.verify.math.derived

*The inverse of the identity stays in a subgroup.*

**Source.** dummit-foote — *Abstract Algebra*, §2.2

## Derived fact 1 — inv(1) in H for every subgroup H

**Coordinate.** Subgroup · inverse · identity inverse stays in the subgroup · **Derived fact**

*Source: dummit-foote*

*Built on: subgroup inverses stay in the subgroup, for inverse on Subgroup, subgroups contain the identity, for membership on Subgroup*

> **Goal.** inv(1) in H for every subgroup H
>
> $$\forall H \in Subgroup\quad inv(1) in H$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that identity inverse stays in the subgroup for inverse on Subgroup. |  |  |
| ② | We split into exhaustive cases — the claim must hold in each one. |  |  |
| ③ | Case 1 (see step 2): suppose 1 in H. |  |  |
| ④ | We invoke the derived fact governing inverse on Subgroup: subgroup inverses stay in the subgroup, for inverse on Subgroup (instantiated for H, 1). |  |  |
| ⑤ | We invoke the derived fact governing membership on Subgroup: subgroups contain the identity, for membership on Subgroup (instantiated for H). |  |  |
| ⑥ | From step 3, step 4, and step 5, this implies inv(1) in H. Together with the other cases (step 3), the goal is discharged. Hence proven. | ⑥ | $inv(1) in H$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ③ | step 2 |
| ⑥ | step 3, step 4, and step 5 |

`Subgroup · inverse · identity inverse stays in the subgroup`
