# examples.verify.math.derived

*Squaring three is self-multiplication.*

**Source.** peano — https://en.wikipedia.org/wiki/Square_(algebra)

## Derived fact 1 — sq(3) = 3 * 3

**Coordinate.** the natural numbers · square · squaring three is self multiplication · **Derived fact**

*Source: peano*

*Built on: squaring is self-multiplication, for square on the natural numbers*

> **Goal.** sq(3) = 3 * 3
>
> $$sq(three) = three^{2}$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that squaring three is self multiplication for square on the natural numbers. |  |  |
| ② | Let three = succ(succ(succ(0))). |  |  |
| ③ | We invoke the definitional clause governing square on the natural numbers: squaring is self-multiplication, for square on the natural numbers (instantiated for three). |  |  |
| ④ | From step 2 and step 3, this implies sq(three) equals three times three. Hence proven. | ④ | $sq(three) = three^{2}$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`the natural numbers · square · squaring three is self multiplication`
