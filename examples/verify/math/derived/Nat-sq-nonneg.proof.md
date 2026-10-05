# examples.verify.math.derived

*The square of a natural number is never negative.*

**Source.** peano — https://en.wikipedia.org/wiki/Square_(algebra)

## Derived fact 1 — n * n ≥ 0 for every natural n

**Coordinate.** the natural numbers · square · squaring never yields a negative · **Derived fact**

*Source: peano — https://en.wikipedia.org/wiki/Ordered_ring*

*Built on: squaring is self-multiplication, for square on the natural numbers, less-or-equal is reflexive, for order on the natural numbers*

> **Goal.** n * n ≥ 0 for every natural n
>
> $$\forall n \in \mathbb{N}\quad sq \ge 0$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that squaring never yields a negative for square on the natural numbers. |  |  |
| ② | Let sq = n * n. |  |  |
| ③ | We invoke the derived fact governing order on the natural numbers: less-or-equal is reflexive, for order on the natural numbers (instantiated for sq). |  |  |
| ④ | From step 2 and step 3, this implies sq is at least 0. Hence proven. | ④ | $sq \ge 0$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`the natural numbers · square · squaring never yields a negative`
