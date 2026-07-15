# examples.verify.math.derived

*Conjunction associates: regrouping ands does not change the result.*

**Source.** boole — https://en.wikipedia.org/wiki/Associative_property

## Derived fact 1 — (a ∧ b) ∧ c = a ∧ (b ∧ c)

**Coordinate.** boolean truth values · conjunction · parentheses do not matter · **Derived fact**

*Source: boole — https://en.wikipedia.org/wiki/Boolean_algebra*

*Built on: order does not matter, for conjunction on boolean truth values*

> **Goal.** (a ∧ b) ∧ c = a ∧ (b ∧ c)
>
> $$\forall a \in \{\mathsf{true}, \mathsf{false}\} \forall b \in \{\mathsf{true}, \mathsf{false}\} \forall c \in \{\mathsf{true}, \mathsf{false}\}\quad (a \land b) \land c = a \land (b \land c)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that parentheses do not matter for conjunction on boolean truth values. |  |  |
| ② | We split into exhaustive cases — the claim must hold in each one. |  |  |
| ③ | Case 1 (see step 2): suppose a holds. |  |  |
| ④ | Case 2 (see step 2): suppose b holds. |  |  |
| ⑤ | From step 4, this implies (the conjunction of a and b) and c equals a and (the conjunction of b and c) in this case. | ⑤ | $(a \land b) \land c = a \land (b \land c)$ |
| ⑥ | Case 3 (see step 2): suppose c holds. |  |  |
| ⑦ | From step 6, this implies (the conjunction of a and b) and c equals a and (the conjunction of b and c) in this case. | ⑦ | $(a \land b) \land c = a \land (b \land c)$ |
| ⑧ | Case 4 (see step 2): neither disjunct holds. |  |  |
| ⑨ | From step 8, this implies (the conjunction of a and b) and c equals a and (the conjunction of b and c) in this case. | ⑨ | $(a \land b) \land c = a \land (b \land c)$ |
| ⑩ | Case 5 (see step 2): suppose b holds. |  |  |
| ⑪ | Case 6 (see step 2): suppose c holds. |  |  |
| ⑫ | From step 11, this implies (the conjunction of a and b) and c equals a and (the conjunction of b and c) in this case. | ⑫ | $(a \land b) \land c = a \land (b \land c)$ |
| ⑬ | Case 7 (see step 2): neither disjunct holds. |  |  |
| ⑭ | From step 13, this implies (the conjunction of a and b) and c equals a and (the conjunction of b and c) in this case. | ⑭ | $(a \land b) \land c = a \land (b \land c)$ |
| ⑮ | Case 8 (see step 2): suppose c holds. |  |  |
| ⑯ | From step 15, this implies (the conjunction of a and b) and c equals a and (the conjunction of b and c) in this case. | ⑯ | $(a \land b) \land c = a \land (b \land c)$ |
| ⑰ | Case 9 (see step 2): neither disjunct holds. |  |  |
| ⑱ | From step 17, this implies (the conjunction of a and b) and c equals a and (the conjunction of b and c). Together with the other cases (step 3, step 4, step 6, step 8, step 10, step 11, step 13, step 15, and step 17), the goal is discharged. Hence proven. | ⑱ | $(a \land b) \land c = a \land (b \land c)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ③ | step 2 |
| ④ | step 2 |
| ⑤ | step 4 |
| ⑥ | step 2 |
| ⑦ | step 6 |
| ⑧ | step 2 |
| ⑨ | step 8 |
| ⑩ | step 2 |
| ⑪ | step 2 |
| ⑫ | step 11 |
| ⑬ | step 2 |
| ⑭ | step 13 |
| ⑮ | step 2 |
| ⑯ | step 15 |
| ⑰ | step 2 |
| ⑱ | step 17 |

`boolean truth values · conjunction · parentheses do not matter`
