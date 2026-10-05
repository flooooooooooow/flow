# examples.verify.math.derived

*Subgroup inverse closure follows from group laws.*

**Source.** dummit-foote — *Abstract Algebra*, §2.2

## Derived fact 1 — If g in H then inv(g) in H when H is a subgroup

**Coordinate.** Subgroup · inverse · subgroup inverses stay in the subgroup · **Derived fact**

*Source: dummit-foote*

*Built on: closed under inverses, for inverse on Subgroup, left inverse recovers the identity, for inverse on Group*

> **Goal.** If g in H then inv(g) in H when H is a subgroup
>
> $$\forall H \in Subgroup \forall g \in Group\quad inv(g) in H$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that subgroup inverses stay in the subgroup for inverse on Subgroup. |  |  |
| ② | We split into exhaustive cases — the claim must hold in each one. |  |  |
| ③ | Case 1 (see step 2): suppose g in H. |  |  |
| ④ | We invoke the definitional clause governing inverse on Subgroup: closed under inverses, for inverse on Subgroup (instantiated for H, g). |  |  |
| ⑤ | We invoke the definitional clause governing inverse on Group: left inverse recovers the identity, for inverse on Group (instantiated for g). |  |  |
| ⑥ | From step 3, step 4, and step 5, this implies inv(g) in H. Together with the other cases (step 3), the goal is discharged. Hence proven. | ⑥ | $inv(g) in H$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ③ | step 2 |
| ⑥ | step 3, step 4, and step 5 |

`Subgroup · inverse · subgroup inverses stay in the subgroup`
