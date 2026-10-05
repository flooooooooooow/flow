# examples.verify.math.derived

*Zero times five is zero for natural numbers.*

**Source.** peano — https://en.wikipedia.org/wiki/Peano_axioms

## Derived fact 1 — 0 * 5 = 0

**Coordinate.** the natural numbers · multiplication · zero times five is zero · **Derived fact**

*Source: peano*

*Built on: zero is the left annihilator, for multiplication on the natural numbers*

> **Goal.** 0 * 5 = 0
>
> $$0 \cdot five = 0$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that zero times five is zero for multiplication on the natural numbers. |  |  |
| ② | Let five = succ(succ(succ(succ(succ(0))))). |  |  |
| ③ | We invoke the definitional clause governing multiplication on the natural numbers: zero is the left annihilator, for multiplication on the natural numbers (instantiated for five). |  |  |
| ④ | From step 2 and step 3, this implies 0 times five equals 0. Hence proven. | ④ | $0 \cdot five = 0$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`the natural numbers · multiplication · zero times five is zero`
