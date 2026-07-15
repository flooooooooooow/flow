# examples.verify.math.derived

*Squaring one gives one.*

**Source.** peano — https://en.wikipedia.org/wiki/Square_(algebra)

## Derived fact 1 — sq(1) = 1, i

**Coordinate.** the natural numbers · square · squaring one gives one · **Derived fact**

*Source: peano*

*Built on: squaring is self-multiplication, for square on the natural numbers, one times one is one, for multiplication on the natural numbers*

> **Goal.** sq(1) = 1, i.e. succ(0) * succ(0) = succ(0)
>
> $$n^{2} = n$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that squaring one gives one for square on the natural numbers. |  |  |
| ② | Let n = succ(0). |  |  |
| ③ | We invoke the definitional clause governing square on the natural numbers: squaring is self-multiplication, for square on the natural numbers (instantiated for n). |  |  |
| ④ | We invoke the derived fact governing multiplication on the natural numbers: one times one is one, for multiplication on the natural numbers. |  |  |
| ⑤ | From step 2, step 3, and step 4, this implies n times n equals n. Hence proven. | ⑤ | $n^{2} = n$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ⑤ | step 2, step 3, and step 4 |

`the natural numbers · square · squaring one gives one`
