# examples.verify.math.derived

*Zero plus one stays in an ideal when zero is present.*

**Source.** dummit-foote — *Abstract Algebra*, §7.3

## Derived fact 1 — If 0 in I then 0 + 1 in I

**Coordinate.** Ideal · addition · zero plus one stays in the ideal · **Derived fact**

*Source: dummit-foote*

*Built on: ideal sums stay in the ideal, for addition on Ideal, ideals contain zero, for membership on Ideal, zero plus one is one, for addition on Ring*

> **Goal.** If 0 in I then 0 + 1 in I
>
> $$\forall I \in Ideal\quad 0 + 1 in I$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that zero plus one stays in the ideal for addition on Ideal. |  |  |
| ② | We split into exhaustive cases — the claim must hold in each one. |  |  |
| ③ | Case 1 (see step 2): suppose 0 in I. |  |  |
| ④ | We invoke the derived fact governing addition on Ideal: ideal sums stay in the ideal, for addition on Ideal (instantiated for I, 0, 1). |  |  |
| ⑤ | We invoke the derived fact governing membership on Ideal: ideals contain zero, for membership on Ideal (instantiated for I). |  |  |
| ⑥ | We invoke the derived fact governing addition on Ring: zero plus one is one, for addition on Ring. |  |  |
| ⑦ | From step 3, step 4, step 5, and step 6, this implies 0 plus 1 in I. Together with the other cases (step 3), the goal is discharged. Hence proven. | ⑦ | $0 + 1 in I$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ③ | step 2 |
| ⑦ | step 3, step 4, step 5, and step 6 |

`Ideal · addition · zero plus one stays in the ideal`
