# examples.verify.math.derived

*The identity element of a monoid is unique.*

**Source.** dummit-foote — *Abstract Algebra*, §1.1

## Derived fact 1 — If e and e' are both identities then e = e'

**Coordinate.** Monoid · identity · the identity is unique · **Derived fact**

*Source: dummit-foote*

*Built on: one is the left identity, for identity on Monoid, one is the right identity, for identity on Monoid, parentheses do not matter, for multiplication on Monoid*

> **Goal.** If e and e' are both identities then e = e'
>
> $$\forall e \in Monoid \forall e_prime \in Monoid\quad e = \text{e prime}$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that the identity is unique for identity on Monoid. |  |  |
| ② | We split into exhaustive cases — the claim must hold in each one. |  |  |
| ③ | Case 1 (see step 2): suppose e * e_prime  equals  e_prime. |  |  |
| ④ | Case 2 (see step 2): suppose e_prime * e  equals  e. |  |  |
| ⑤ | We invoke the definitional clause governing identity on Monoid: one is the left identity, for identity on Monoid (instantiated for e_prime). |  |  |
| ⑥ | We invoke the definitional clause governing identity on Monoid: one is the right identity, for identity on Monoid (instantiated for e). |  |  |
| ⑦ | We invoke the definitional clause governing multiplication on Monoid: parentheses do not matter, for multiplication on Monoid (instantiated for e, e_prime, e). |  |  |
| ⑧ | From step 4, step 5, step 6, and step 7, this implies e equals e prime. Together with the other cases (step 3 and step 4), the goal is discharged. Hence proven. | ⑧ | $e = \text{e prime}$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ③ | step 2 |
| ④ | step 2 |
| ⑧ | step 4, step 5, step 6, and step 7 |

`Monoid · identity · the identity is unique`
