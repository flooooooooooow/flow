# examples.verify.math.derived

*Three plus zero is three for natural numbers.*

**Source.** peano — https://en.wikipedia.org/wiki/Peano_axioms

## Derived fact 1 — 3 + 0 = 3

**Coordinate.** the natural numbers · addition · three plus zero is three · **Derived fact**

*Source: peano*

*Built on: adding zero on the right does not change the number*

> **Goal.** 3 + 0 = 3
>
> $$three + 0 = three$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that three plus zero is three for addition on the natural numbers. |  |  |
| ② | Let three = succ(succ(succ(0))). |  |  |
| ③ | We invoke the derived fact governing addition on the natural numbers: adding zero on the right does not change the number (instantiated for three). | ③ | $three + 0 = three$ |
| ④ | From step 2 and step 3, this implies three plus 0 equals three. Hence proven. | ④ | $three + 0 = three$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`the natural numbers · addition · three plus zero is three`
