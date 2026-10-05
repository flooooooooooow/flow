# examples.verify.math.derived

*Zero times four is zero for natural numbers.*

**Source.** peano — https://en.wikipedia.org/wiki/Peano_axioms

## Derived fact 1 — 0 * 4 = 0

**Coordinate.** the natural numbers · multiplication · zero times four is zero · **Derived fact**

*Source: peano*

*Built on: zero is the left annihilator, for multiplication on the natural numbers*

> **Goal.** 0 * 4 = 0
>
> $$0 \cdot four = 0$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that zero times four is zero for multiplication on the natural numbers. |  |  |
| ② | Let four = succ(succ(succ(succ(0)))). |  |  |
| ③ | We invoke the definitional clause governing multiplication on the natural numbers: zero is the left annihilator, for multiplication on the natural numbers (instantiated for four). |  |  |
| ④ | From step 2 and step 3, this implies 0 times four equals 0. Hence proven. | ④ | $0 \cdot four = 0$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`the natural numbers · multiplication · zero times four is zero`
