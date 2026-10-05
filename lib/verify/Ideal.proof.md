# verify.Ideal

*Ring ideal axioms as a subring closed under absorption.*

**Source.** dummit-foote — *Abstract Algebra*, §7.3

## Definition 1 — An ideal contains the ring zero

**Coordinate.** Ideal · membership · zero lies in every ideal · **Definition**

*Source: dummit-foote*

> **Goal.** An ideal contains the ring zero
>
> $$\forall I \in Ideal\quad 0 in I$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We stipulate zero lies in every ideal for membership on Ideal — this is a definition, not a derived fact. |  |  |
| ② | This follows directly from the definition: 0 in I. Hence proven. | ② | $0 in I$ |

`Ideal · membership · zero lies in every ideal`

## Definition 2 — An ideal is closed under addition

**Coordinate.** Ideal · addition · closed under addition · **Definition**

*Source: dummit-foote*

> **Goal.** An ideal is closed under addition
>
> $$\forall I \in Ideal \forall a \in Ring \forall b \in Ring\quad a + b in I$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We stipulate closed under addition for addition on Ideal — this is a definition, not a derived fact. |  |  |
| ② | We split into exhaustive cases — the claim must hold in each one. |  |  |
| ③ | Case 1 (see step 2): suppose a in I. |  |  |
| ④ | Case 2 (see step 2): suppose b in I. |  |  |
| ⑤ | From step 4, this implies a plus b in I. Together with the other cases (step 3 and step 4), the goal is discharged. Hence proven. | ⑤ | $a + b in I$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ③ | step 2 |
| ④ | step 2 |
| ⑤ | step 4 |

`Ideal · addition · closed under addition`
