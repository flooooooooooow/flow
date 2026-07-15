# examples.verify.math.derived

*Zero on the right annihilates natural multiplication.*

**Source.** peano — https://en.wikipedia.org/wiki/Peano_axioms

## Derived fact 1 — n * 0 = 0

**Coordinate.** the natural numbers · multiplication · zero on the right gives zero · **Derived fact**

*Source: peano*

*Built on: zero is the left annihilator, for multiplication on the natural numbers, order does not matter, for multiplication on the natural numbers*

> **Goal.** n * 0 = 0
>
> $$\forall n \in \mathbb{N}\quad n \cdot 0 = 0$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that zero on the right gives zero for multiplication on the natural numbers. |  |  |
| ② | We invoke the definitional clause governing multiplication on the natural numbers: zero is the left annihilator, for multiplication on the natural numbers (instantiated for n). |  |  |
| ③ | We invoke the derived fact governing multiplication on the natural numbers: order does not matter, for multiplication on the natural numbers (instantiated for n, 0). |  |  |
| ④ | From step 2 and step 3, this implies n times 0 equals 0. Hence proven. | ④ | $n \cdot 0 = 0$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`the natural numbers · multiplication · zero on the right gives zero`
