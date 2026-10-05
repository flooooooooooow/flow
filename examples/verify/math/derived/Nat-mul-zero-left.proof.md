# examples.verify.math.derived

*Zero on the left annihilates multiplication.*

**Source.** peano — https://en.wikipedia.org/wiki/Peano_axioms

## Derived fact 1 — 0 * n = 0

**Coordinate.** the natural numbers · multiplication · zero on the left gives zero · **Derived fact**

*Source: peano*

*Built on: zero is the left annihilator, for multiplication on the natural numbers, zero is the right annihilator, for multiplication on the natural numbers, order does not matter, for multiplication on the natural numbers*

> **Goal.** 0 * n = 0
>
> $$\forall n \in \mathbb{N}\quad 0 \cdot n = 0$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that zero on the left gives zero for multiplication on the natural numbers. |  |  |
| ② | We invoke the definitional clause governing multiplication on the natural numbers: zero is the left annihilator, for multiplication on the natural numbers (instantiated for n). |  |  |
| ③ | We invoke the definitional clause governing multiplication on the natural numbers: zero is the right annihilator, for multiplication on the natural numbers (instantiated for 0). |  |  |
| ④ | We invoke the derived fact governing multiplication on the natural numbers: order does not matter, for multiplication on the natural numbers (instantiated for 0, n). |  |  |
| ⑤ | From step 2, step 3, and step 4, this implies 0 times n equals 0. Hence proven. | ⑤ | $0 \cdot n = 0$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ⑤ | step 2, step 3, and step 4 |

`the natural numbers · multiplication · zero on the left gives zero`
