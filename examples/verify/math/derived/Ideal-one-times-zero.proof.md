# examples.verify.math.derived

*One times zero stays in an ideal.*

**Source.** dummit-foote — *Abstract Algebra*, §7.3

## Derived fact 1 — If 0 in I then 1 * 0 in I

**Coordinate.** Ideal · multiplication · one times zero stays in the ideal · **Derived fact**

*Source: dummit-foote*

*Built on: zero product stays in the ideal, for multiplication on Ideal, ideals contain zero, for membership on Ideal*

> **Goal.** If 0 in I then 1 * 0 in I
>
> $$\forall I \in Ideal\quad 1 \cdot 0 in I$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that one times zero stays in the ideal for multiplication on Ideal. |  |  |
| ② | We split into exhaustive cases — the claim must hold in each one. |  |  |
| ③ | Case 1 (see step 2): suppose 0 in I. |  |  |
| ④ | We invoke the derived fact governing multiplication on Ideal: zero product stays in the ideal, for multiplication on Ideal (instantiated for I, 1). |  |  |
| ⑤ | We invoke the derived fact governing membership on Ideal: ideals contain zero, for membership on Ideal (instantiated for I). |  |  |
| ⑥ | From step 3, step 4, and step 5, this implies 1 times 0 in I. Together with the other cases (step 3), the goal is discharged. Hence proven. | ⑥ | $1 \cdot 0 in I$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ③ | step 2 |
| ⑥ | step 3, step 4, and step 5 |

`Ideal · multiplication · one times zero stays in the ideal`
