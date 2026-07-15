# examples.verify.math.derived

*Squaring a successor expands by self-multiplication.*

**Source.** peano — https://en.wikipedia.org/wiki/Square_(algebra)

## Derived fact 1 — sq(succ(n)) = succ(n) * succ(n)

**Coordinate.** the natural numbers · square · successor squares by self multiplication · **Derived fact**

*Source: peano*

*Built on: squaring is self-multiplication, for square on the natural numbers, successor on the right via commutativity, for addition on the natural numbers*

> **Goal.** sq(succ(n)) = succ(n) * succ(n)
>
> $$\forall n \in \mathbb{N}\quad sq(s) = s^{2}$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that successor squares by self multiplication for square on the natural numbers. |  |  |
| ② | Let s = succ(n). |  |  |
| ③ | We invoke the definitional clause governing square on the natural numbers: squaring is self-multiplication, for square on the natural numbers (instantiated for s). |  |  |
| ④ | We invoke the derived fact governing addition on the natural numbers: successor on the right via commutativity, for addition on the natural numbers (instantiated for n, 0). |  |  |
| ⑤ | From step 2, step 3, and step 4, this implies sq(s) equals s times s. Hence proven. | ⑤ | $sq(s) = s^{2}$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ⑤ | step 2, step 3, and step 4 |

`the natural numbers · square · successor squares by self multiplication`
