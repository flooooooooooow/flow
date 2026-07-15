# examples.verify.math.derived

*One plus zero stays in an ideal.*

**Source.** dummit-foote — *Abstract Algebra*, §7.3

## Derived fact 1 — If 0 in I then 1 + 0 in I

**Coordinate.** Ideal · addition · one plus zero stays in the ideal · **Derived fact**

*Source: dummit-foote*

*Built on: one times zero stays in the ideal, for multiplication on Ideal, ideals contain zero, for membership on Ideal, one plus zero is one, for addition on Ring*

> **Goal.** If 0 in I then 1 + 0 in I
>
> $$\forall I \in Ideal\quad 1 + 0 in I$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that one plus zero stays in the ideal for addition on Ideal. |  |  |
| ② | We split into exhaustive cases — the claim must hold in each one. |  |  |
| ③ | Case 1 (see step 2): suppose 0 in I. |  |  |
| ④ | We invoke the derived fact governing multiplication on Ideal: one times zero stays in the ideal, for multiplication on Ideal (instantiated for I). |  |  |
| ⑤ | We invoke the derived fact governing membership on Ideal: ideals contain zero, for membership on Ideal (instantiated for I). |  |  |
| ⑥ | We invoke the derived fact governing addition on Ring: one plus zero is one, for addition on Ring. |  |  |
| ⑦ | From step 3, step 4, step 5, and step 6, this implies 1 plus 0 in I. Together with the other cases (step 3), the goal is discharged. Hence proven. | ⑦ | $1 + 0 in I$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ③ | step 2 |
| ⑦ | step 3, step 4, step 5, and step 6 |

`Ideal · addition · one plus zero stays in the ideal`
