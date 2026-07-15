# examples.verify.math.derived

*Squaring two is four-fold self-multiplication.*

**Source.** peano — https://en.wikipedia.org/wiki/Square_(algebra)

## Derived fact 1 — sq(2) = 2 * 2

**Coordinate.** the natural numbers · square · squaring two is self multiplication · **Derived fact**

*Source: peano*

*Built on: squaring is self-multiplication, for square on the natural numbers*

> **Goal.** sq(2) = 2 * 2
>
> $$sq(two) = two^{2}$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that squaring two is self multiplication for square on the natural numbers. |  |  |
| ② | Let two = succ(succ(0)). |  |  |
| ③ | We invoke the definitional clause governing square on the natural numbers: squaring is self-multiplication, for square on the natural numbers (instantiated for two). |  |  |
| ④ | From step 2 and step 3, this implies sq(two) equals two times two. Hence proven. | ④ | $sq(two) = two^{2}$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`the natural numbers · square · squaring two is self multiplication`
