# examples.verify.math.derived

*Zero plus zero stays in an ideal.*

**Source.** dummit-foote — *Abstract Algebra*, §7.3

## Derived fact 1 — If 0 in I then 0 + 0 in I

**Coordinate.** Ideal · addition · zero plus zero stays in the ideal derived · **Derived fact**

*Source: dummit-foote*

*Built on: ideal sums stay in the ideal, for addition on Ideal, ideals contain zero, for membership on Ideal*

> **Goal.** If 0 in I then 0 + 0 in I
>
> $$\forall I \in Ideal\quad 0 + 0 in I$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that zero plus zero stays in the ideal derived for addition on Ideal. |  |  |
| ② | We split into exhaustive cases — the claim must hold in each one. |  |  |
| ③ | Case 1 (see step 2): suppose 0 in I. |  |  |
| ④ | We invoke the derived fact governing addition on Ideal: ideal sums stay in the ideal, for addition on Ideal (instantiated for I, 0, 0). |  |  |
| ⑤ | We invoke the derived fact governing membership on Ideal: ideals contain zero, for membership on Ideal (instantiated for I). |  |  |
| ⑥ | From step 3, step 4, and step 5, this implies 0 plus 0 in I. Together with the other cases (step 3), the goal is discharged. Hence proven. | ⑥ | $0 + 0 in I$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ③ | step 2 |
| ⑥ | step 3, step 4, and step 5 |

`Ideal · addition · zero plus zero stays in the ideal derived`
