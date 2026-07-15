# examples.verify.math.derived

*Disjunction associates: regrouping ors does not change the result.*

**Source.** boole — https://en.wikipedia.org/wiki/Associative_property

## Derived fact 1 — (a ∨ b) ∨ c = a ∨ (b ∨ c)

**Coordinate.** boolean truth values · disjunction · parentheses do not matter · **Derived fact**

*Source: boole — https://en.wikipedia.org/wiki/Boolean_algebra*

*Built on: order does not matter for "or"*

> **Goal.** (a ∨ b) ∨ c = a ∨ (b ∨ c)
>
> $$\forall a \in \{\mathsf{true}, \mathsf{false}\} \forall b \in \{\mathsf{true}, \mathsf{false}\} \forall c \in \{\mathsf{true}, \mathsf{false}\}\quad (a \lor b) \lor c = a \lor (b \lor c)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that parentheses do not matter for disjunction on boolean truth values. |  |  |
| ② | We split into exhaustive cases — the claim must hold in each one. |  |  |
| ③ | Case 1 (see step 2): suppose a holds. |  |  |
| ④ | From step 3, this implies (the disjunction of a and b) or c equals a or (the disjunction of b and c) in this case. | ④ | $(a \lor b) \lor c = a \lor (b \lor c)$ |
| ⑤ | Case 2 (see step 2): suppose b holds. |  |  |
| ⑥ | From step 5, this implies (the disjunction of a and b) or c equals a or (the disjunction of b and c) in this case. | ⑥ | $(a \lor b) \lor c = a \lor (b \lor c)$ |
| ⑦ | Case 3 (see step 2): suppose c holds. |  |  |
| ⑧ | From step 7, this implies (the disjunction of a and b) or c equals a or (the disjunction of b and c) in this case. | ⑧ | $(a \lor b) \lor c = a \lor (b \lor c)$ |
| ⑨ | Case 4 (see step 2): neither disjunct holds. |  |  |
| ⑩ | From step 9, this implies (the disjunction of a and b) or c equals a or (the disjunction of b and c). Together with the other cases (step 3, step 5, step 7, and step 9), the goal is discharged. Hence proven. | ⑩ | $(a \lor b) \lor c = a \lor (b \lor c)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ③ | step 2 |
| ④ | step 3 |
| ⑤ | step 2 |
| ⑥ | step 5 |
| ⑦ | step 2 |
| ⑧ | step 7 |
| ⑨ | step 2 |
| ⑩ | step 9 |

`boolean truth values · disjunction · parentheses do not matter`
