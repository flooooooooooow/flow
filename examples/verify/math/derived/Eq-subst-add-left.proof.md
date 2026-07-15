# examples.verify.math.derived

*Equal summands stay equal when the same term is added on the left.*

**Source.** leibniz — https://en.wikipedia.org/wiki/Substitution_(logic)

## Derived fact 1 — From a = b we deduce c + a = c + b

**Coordinate.** equality · equality · equal terms add the same on the left · **Derived fact**

*Source: peano/induction — Gries & Schneider, Ch. 3*

*Built on: you can swap the order when you add, equal terms add the same on the right, for equality on equality*

> **Goal.** From a = b we deduce c + a = c + b
>
> $$\forall a \in \mathbb{N} \forall b \in \mathbb{N} \forall c \in \mathbb{N}\quad c + a = c + b$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that equal terms add the same on the left for equality on equality. |  |  |
| ② | We split into exhaustive cases — the claim must hold in each one. |  |  |
| ③ | Case 1 (see step 2): suppose a  equals  b. |  |  |
| ④ | We invoke the derived fact governing addition on the natural numbers: you can swap the order when you add (instantiated for a, c). | ④ | $a + c = c + a$ |
| ⑤ | We invoke the derived fact governing equality on equality: equal terms add the same on the right, for equality on equality (instantiated for a, b, c). |  |  |
| ⑥ | From step 3, step 4, and step 5, this implies c plus a equals c plus b. Together with the other cases (step 3), the goal is discharged. Hence proven. | ⑥ | $c + a = c + b$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ③ | step 2 |
| ⑥ | step 3, step 4, and step 5 |

`equality · equality · equal terms add the same on the left`
