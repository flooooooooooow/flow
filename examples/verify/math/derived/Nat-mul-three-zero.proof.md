# examples.verify.math.derived

*Three times zero is zero for natural numbers.*

**Source.** peano — https://en.wikipedia.org/wiki/Peano_axioms

## Derived fact 1 — 3 * 0 = 0

**Coordinate.** the natural numbers · multiplication · three times zero is zero · **Derived fact**

*Source: peano*

*Built on: zero is the right annihilator, for multiplication on the natural numbers*

> **Goal.** 3 * 0 = 0
>
> $$three \cdot 0 = 0$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that three times zero is zero for multiplication on the natural numbers. |  |  |
| ② | Let three = succ(succ(succ(0))). |  |  |
| ③ | We invoke the definitional clause governing multiplication on the natural numbers: zero is the right annihilator, for multiplication on the natural numbers (instantiated for three). |  |  |
| ④ | From step 2 and step 3, this implies three times 0 equals 0. Hence proven. | ④ | $three \cdot 0 = 0$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`the natural numbers · multiplication · three times zero is zero`
