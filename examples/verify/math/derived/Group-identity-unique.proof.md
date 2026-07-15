# examples.verify.math.derived

*The identity element of a group is unique.*

**Source.** dummit-foote — *Abstract Algebra*, §1.1

## Derived fact 1 — If e and e' are both identities then e = e'

**Coordinate.** Group · identity · the identity is unique · **Derived fact**

*Source: dummit-foote*

*Built on: one is the left identity, for identity on Group, one is the right identity, for identity on Group, parentheses do not matter, for multiplication on Group*

> **Goal.** If e and e' are both identities then e = e'
>
> $$\forall e \in Group \forall e_prime \in Group\quad e = \text{e prime}$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that the identity is unique for identity on Group. |  |  |
| ② | We split into exhaustive cases — the claim must hold in each one. |  |  |
| ③ | Case 1 (see step 2): suppose e * e_prime  equals  e_prime. |  |  |
| ④ | Case 2 (see step 2): suppose e_prime * e  equals  e. |  |  |
| ⑤ | We invoke the definitional clause governing identity on Group: one is the left identity, for identity on Group (instantiated for e_prime). |  |  |
| ⑥ | We invoke the definitional clause governing identity on Group: one is the right identity, for identity on Group (instantiated for e). |  |  |
| ⑦ | We invoke the definitional clause governing multiplication on Group: parentheses do not matter, for multiplication on Group (instantiated for e, e_prime, e). |  |  |
| ⑧ | From step 4, step 5, step 6, and step 7, this implies e equals e prime. Together with the other cases (step 3 and step 4), the goal is discharged. Hence proven. | ⑧ | $e = \text{e prime}$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ③ | step 2 |
| ④ | step 2 |
| ⑧ | step 4, step 5, step 6, and step 7 |

`Group · identity · the identity is unique`
