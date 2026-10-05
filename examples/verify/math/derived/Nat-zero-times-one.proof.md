# examples.verify.math.derived

*Zero times one is zero for natural numbers.*

**Source.** peano — https://en.wikipedia.org/wiki/Peano_axioms

## Derived fact 1 — 0 * 1 = 0

**Coordinate.** the natural numbers · multiplication · zero times one is zero · **Derived fact**

*Source: peano*

*Built on: zero is the left annihilator, for multiplication on the natural numbers*

> **Goal.** 0 * 1 = 0
>
> $$0 * \mathrm{succ}(0) = 0$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that zero times one is zero for multiplication on the natural numbers. |  |  |
| ② | We invoke the definitional clause governing multiplication on the natural numbers: zero is the left annihilator, for multiplication on the natural numbers (instantiated for succ(0)). |  |  |
| ③ | From step 2, this implies 0 times the successor of 0 equals 0. Hence proven. | ③ | $0 * \mathrm{succ}(0) = 0$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ③ | step 2 |

`the natural numbers · multiplication · zero times one is zero`
