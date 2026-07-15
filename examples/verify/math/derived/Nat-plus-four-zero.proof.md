# examples.verify.math.derived

*Four plus zero is four for natural numbers.*

**Source.** peano — https://en.wikipedia.org/wiki/Peano_axioms

## Derived fact 1 — 4 + 0 = 4

**Coordinate.** the natural numbers · addition · four plus zero is four · **Derived fact**

*Source: peano*

*Built on: adding zero on the right does not change the number*

> **Goal.** 4 + 0 = 4
>
> $$four + 0 = four$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that four plus zero is four for addition on the natural numbers. |  |  |
| ② | Let four = succ(succ(succ(succ(0)))). |  |  |
| ③ | We invoke the derived fact governing addition on the natural numbers: adding zero on the right does not change the number (instantiated for four). | ③ | $four + 0 = four$ |
| ④ | From step 2 and step 3, this implies four plus 0 equals four. Hence proven. | ④ | $four + 0 = four$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`the natural numbers · addition · four plus zero is four`
