# examples.verify.math.derived

*Ideal addition closure follows from ideal axioms.*

**Source.** dummit-foote — *Abstract Algebra*, §7.3

## Derived fact 1 — If a in I and b in I then a + b in I when I is an ideal

**Coordinate.** Ideal · addition · ideal sums stay in the ideal · **Derived fact**

*Source: dummit-foote*

*Built on: closed under addition, for addition on Ideal, zero is the left identity, for addition on Ring*

> **Goal.** If a in I and b in I then a + b in I when I is an ideal
>
> $$\forall I \in Ideal \forall a \in Ring \forall b \in Ring\quad a + b in I$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that ideal sums stay in the ideal for addition on Ideal. |  |  |
| ② | We split into exhaustive cases — the claim must hold in each one. |  |  |
| ③ | Case 1 (see step 2): suppose a in I. |  |  |
| ④ | Case 2 (see step 2): suppose b in I. |  |  |
| ⑤ | We invoke the definitional clause governing addition on Ideal: closed under addition, for addition on Ideal (instantiated for I, a, b). |  |  |
| ⑥ | We invoke the definitional clause governing addition on Ring: zero is the left identity, for addition on Ring (instantiated for a). |  |  |
| ⑦ | From step 4, step 5, and step 6, this implies a plus b in I. Together with the other cases (step 3 and step 4), the goal is discharged. Hence proven. | ⑦ | $a + b in I$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ③ | step 2 |
| ④ | step 2 |
| ⑦ | step 4, step 5, and step 6 |

`Ideal · addition · ideal sums stay in the ideal`
