# examples.verify.math.derived

*De Morgan law for disjunction and conjunction.*

**Source.** boole — https://en.wikipedia.org/wiki/De_Morgan%27s_laws

## Derived fact 1 — ¬(a ∨ b) = (¬a) ∧ (¬b)

**Coordinate.** boolean truth values · negation · de Morgan for disjunction and conjunction · **Derived fact**

*Source: boole*

*Built on: double negation returns the value, for negation on boolean truth values*

> **Goal.** ¬(a ∨ b) = (¬a) ∧ (¬b)
>
> $$\forall a \in \{\mathsf{true}, \mathsf{false}\} \forall b \in \{\mathsf{true}, \mathsf{false}\}\quad !(a \lor b) = (!a) \land (!b)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that de Morgan for disjunction and conjunction for negation on boolean truth values. |  |  |
| ② | We split into exhaustive cases — the claim must hold in each one. |  |  |
| ③ | Case 1 (see step 2): suppose a holds. |  |  |
| ④ | Case 2 (see step 2): suppose b holds. |  |  |
| ⑤ | From step 4, this implies !(the disjunction of a and b) equals (!a) and (!b) in this case. | ⑤ | $!(a \lor b) = (!a) \land (!b)$ |
| ⑥ | Case 3 (see step 2): neither disjunct holds. |  |  |
| ⑦ | From step 6, this implies !(the disjunction of a and b) equals (!a) and (!b) in this case. | ⑦ | $!(a \lor b) = (!a) \land (!b)$ |
| ⑧ | Case 4 (see step 2): suppose b holds. |  |  |
| ⑨ | From step 8, this implies !(the disjunction of a and b) equals (!a) and (!b) in this case. | ⑨ | $!(a \lor b) = (!a) \land (!b)$ |
| ⑩ | Case 5 (see step 2): neither disjunct holds. |  |  |
| ⑪ | From step 10, this implies !(the disjunction of a and b) equals (!a) and (!b). Together with the other cases (step 3, step 4, step 6, step 8, and step 10), the goal is discharged. Hence proven. | ⑪ | $!(a \lor b) = (!a) \land (!b)$ |

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
| ⑪ | step 10 |

`boolean truth values · negation · de Morgan for disjunction and conjunction`
