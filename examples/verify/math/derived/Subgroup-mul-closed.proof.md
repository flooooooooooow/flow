# examples.verify.math.derived

*Subgroup multiplication closure follows from subgroup axioms.*

**Source.** dummit-foote — *Abstract Algebra*, §2.2

## Derived fact 1 — If a in H and b in H then a * b in H when H is a subgroup

**Coordinate.** Subgroup · multiplication · subgroup products stay in the subgroup · **Derived fact**

*Source: dummit-foote*

*Built on: closed under multiplication, for multiplication on Subgroup, one is the left identity, for identity on Group*

> **Goal.** If a in H and b in H then a * b in H when H is a subgroup
>
> $$\forall H \in Subgroup \forall a \in Group \forall b \in Group\quad a \cdot b in H$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that subgroup products stay in the subgroup for multiplication on Subgroup. |  |  |
| ② | We split into exhaustive cases — the claim must hold in each one. |  |  |
| ③ | Case 1 (see step 2): suppose a in H. |  |  |
| ④ | Case 2 (see step 2): suppose b in H. |  |  |
| ⑤ | We invoke the definitional clause governing multiplication on Subgroup: closed under multiplication, for multiplication on Subgroup (instantiated for H, a, b). |  |  |
| ⑥ | We invoke the definitional clause governing identity on Group: one is the left identity, for identity on Group (instantiated for a). |  |  |
| ⑦ | From step 4, step 5, and step 6, this implies a times b in H. Together with the other cases (step 3 and step 4), the goal is discharged. Hence proven. | ⑦ | $a \cdot b in H$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ③ | step 2 |
| ④ | step 2 |
| ⑦ | step 4, step 5, and step 6 |

`Subgroup · multiplication · subgroup products stay in the subgroup`
