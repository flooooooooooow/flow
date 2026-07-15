# examples.verify.math.derived

*Multiplying two by itself equals its square.*

**Source.** peano — https://en.wikipedia.org/wiki/Square_(algebra)

## Derived fact 1 — 2 * 2 = sq(2)

**Coordinate.** the natural numbers · multiplication · two times two is the square of two · **Derived fact**

*Source: peano*

*Built on: squaring two is self multiplication, for square on the natural numbers*

> **Goal.** 2 * 2 = sq(2)
>
> $$two^{2} = sq(two)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that two times two is the square of two for multiplication on the natural numbers. |  |  |
| ② | Let two = succ(succ(0)). |  |  |
| ③ | We invoke the derived fact governing square on the natural numbers: squaring two is self multiplication, for square on the natural numbers. |  |  |
| ④ | From step 2 and step 3, this implies two times two equals sq(two). Hence proven. | ④ | $two^{2} = sq(two)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`the natural numbers · multiplication · two times two is the square of two`
