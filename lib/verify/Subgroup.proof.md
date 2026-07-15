# verify.Subgroup

*Subgroup axioms as a subset closed under multiplication and inverses.*

**Source.** dummit-foote — *Abstract Algebra*, §2.2

## Definition 1 — A subgroup contains the group identity

**Coordinate.** Subgroup · membership · the identity lies in every subgroup · **Definition**

*Source: dummit-foote*

> **Goal.** A subgroup contains the group identity
>
> $$\forall H \in Subgroup\quad 1 in H$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We stipulate the identity lies in every subgroup for membership on Subgroup — this is a definition, not a derived fact. |  |  |
| ② | This follows directly from the definition: 1 in H. Hence proven. | ② | $1 in H$ |

`Subgroup · membership · the identity lies in every subgroup`

## Definition 2 — A subgroup is closed under multiplication

**Coordinate.** Subgroup · multiplication · closed under multiplication · **Definition**

*Source: dummit-foote*

> **Goal.** A subgroup is closed under multiplication
>
> $$\forall H \in Subgroup \forall a \in Group \forall b \in Group\quad a \cdot b in H$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We stipulate closed under multiplication for multiplication on Subgroup — this is a definition, not a derived fact. |  |  |
| ② | We split into exhaustive cases — the claim must hold in each one. |  |  |
| ③ | Case 1 (see step 2): suppose a in H. |  |  |
| ④ | Case 2 (see step 2): suppose b in H. |  |  |
| ⑤ | From step 4, this implies a times b in H. Together with the other cases (step 3 and step 4), the goal is discharged. Hence proven. | ⑤ | $a \cdot b in H$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ③ | step 2 |
| ④ | step 2 |
| ⑤ | step 4 |

`Subgroup · multiplication · closed under multiplication`

## Definition 3 — A subgroup is closed under taking inverses

**Coordinate.** Subgroup · inverse · closed under inverses · **Definition**

*Source: dummit-foote*

> **Goal.** A subgroup is closed under taking inverses
>
> $$\forall H \in Subgroup \forall g \in Group\quad inv(g) in H$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We stipulate closed under inverses for inverse on Subgroup — this is a definition, not a derived fact. |  |  |
| ② | We split into exhaustive cases — the claim must hold in each one. |  |  |
| ③ | Case 1 (see step 2): suppose g in H. |  |  |
| ④ | From step 3, this implies inv(g) in H. Together with the other cases (step 3), the goal is discharged. Hence proven. | ④ | $inv(g) in H$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ③ | step 2 |
| ④ | step 3 |

`Subgroup · inverse · closed under inverses`
