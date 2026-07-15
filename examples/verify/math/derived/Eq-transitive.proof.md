# examples.verify.math.derived

*Equalities chain: x = y and y = z imply x = z.*

**Source.** leibniz — https://en.wikipedia.org/wiki/Transitive_relation

## Derived fact 1 — If x equals y and y equals z, then x equals z

**Coordinate.** equality · equality · equality chains · **Derived fact**

*Source: leibniz — https://en.wikipedia.org/wiki/Transitive_relation*

*Built on: anything is always equal to itself*

> **Goal.** If x equals y and y equals z, then x equals z
>
> $$\forall x \in \mathbb{N} \forall y \in \mathbb{N} \forall z \in \mathbb{N}\quad x = z$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that equality chains for equality on equality. |  |  |
| ② | We split into exhaustive cases — the claim must hold in each one. |  |  |
| ③ | Case 1 (see step 2): suppose x  equals  y. |  |  |
| ④ | Case 2 (see step 2): suppose y  equals  z. |  |  |
| ⑤ | We invoke the axiom governing equality on equality: anything is always equal to itself (instantiated for x). | ⑤ | $x = x$ |
| ⑥ | We invoke the axiom governing equality on equality: anything is always equal to itself (instantiated for z). | ⑥ | $z = z$ |
| ⑦ | From step 4, step 5, and step 6, this implies x equals z. Together with the other cases (step 3 and step 4), the goal is discharged. Hence proven. | ⑦ | $x = z$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ③ | step 2 |
| ④ | step 2 |
| ⑦ | step 4, step 5, and step 6 |

`equality · equality · equality chains`
