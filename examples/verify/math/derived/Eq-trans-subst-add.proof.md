# examples.verify.math.derived

*Transitive equality preserves right addition.*

**Source.** leibniz — https://en.wikipedia.org/wiki/Substitution_(logic)

## Derived fact 1 — If a = b and b = c then a + d = c + d

**Coordinate.** equality · equality · transitive substitution on the right · **Derived fact**

*Source: leibniz*

*Built on: equal terms add the same on the right, for equality on equality, equality reverses, for equality on equality*

> **Goal.** If a = b and b = c then a + d = c + d
>
> $$\forall a \in \mathbb{N} \forall b \in \mathbb{N} \forall c \in \mathbb{N} \forall d \in \mathbb{N}\quad a + d = c + d$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that transitive substitution on the right for equality on equality. |  |  |
| ② | We split into exhaustive cases — the claim must hold in each one. |  |  |
| ③ | Case 1 (see step 2): suppose a  equals  b. |  |  |
| ④ | Case 2 (see step 2): suppose b  equals  c. |  |  |
| ⑤ | We invoke the derived fact governing equality on equality: equal terms add the same on the right, for equality on equality (instantiated for a, b, d). |  |  |
| ⑥ | We invoke the derived fact governing equality on equality: equality reverses, for equality on equality (instantiated for b, c). |  |  |
| ⑦ | We invoke the derived fact governing equality on equality: equal terms add the same on the right, for equality on equality (instantiated for b, c, d). |  |  |
| ⑧ | From step 4, step 5, step 6, and step 7, this implies a plus d equals c plus d. Together with the other cases (step 3 and step 4), the goal is discharged. Hence proven. | ⑧ | $a + d = c + d$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ③ | step 2 |
| ④ | step 2 |
| ⑧ | step 4, step 5, step 6, and step 7 |

`equality · equality · transitive substitution on the right`
