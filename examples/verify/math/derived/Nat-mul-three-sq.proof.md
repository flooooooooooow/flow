# examples.verify.math.derived

*Three times three equals its square.*

**Source.** peano — https://en.wikipedia.org/wiki/Square_(algebra)

## Derived fact 1 — 3 * 3 = sq(3)

**Coordinate.** the natural numbers · multiplication · three times three is the square of three · **Derived fact**

*Source: peano*

*Built on: squaring three is self multiplication, for square on the natural numbers*

> **Goal.** 3 * 3 = sq(3)
>
> $$three^{2} = sq(three)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that three times three is the square of three for multiplication on the natural numbers. |  |  |
| ② | Let three = succ(succ(succ(0))). |  |  |
| ③ | We invoke the derived fact governing square on the natural numbers: squaring three is self multiplication, for square on the natural numbers. |  |  |
| ④ | From step 2 and step 3, this implies three times three equals sq(three). Hence proven. | ④ | $three^{2} = sq(three)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`the natural numbers · multiplication · three times three is the square of three`
