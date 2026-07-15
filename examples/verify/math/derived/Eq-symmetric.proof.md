# examples.verify.math.derived

*If two naturals are equal, the equality reads either way.*

**Source.** leibniz — https://en.wikipedia.org/wiki/Identity_(mathematics)#Equality

## Derived fact 1 — Equality reverses: from x = y we obtain y = x

**Coordinate.** equality · equality · equality reverses · **Derived fact**

*Source: leibniz — https://en.wikipedia.org/wiki/Symmetric_relation*

*Built on: anything is always equal to itself*

> **Goal.** Equality reverses: from x = y we obtain y = x
>
> $$\forall x \in \mathbb{N} \forall y \in \mathbb{N}\quad y = x$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that equality reverses for equality on equality. |  |  |
| ② | We split into exhaustive cases — the claim must hold in each one. |  |  |
| ③ | Case 1 (see step 2): suppose x  equals  y. |  |  |
| ④ | We invoke the axiom governing equality on equality: anything is always equal to itself (instantiated for x). | ④ | $x = x$ |
| ⑤ | We invoke the axiom governing equality on equality: anything is always equal to itself (instantiated for y). | ⑤ | $y = y$ |
| ⑥ | From step 3, step 4, and step 5, this implies y equals x. Together with the other cases (step 3), the goal is discharged. Hence proven. | ⑥ | $y = x$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ③ | step 2 |
| ⑥ | step 3, step 4, and step 5 |

`equality · equality · equality reverses`
