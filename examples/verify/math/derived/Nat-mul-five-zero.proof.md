# examples.verify.math.derived

*Five times zero is zero for natural numbers.*

**Source.** peano — https://en.wikipedia.org/wiki/Peano_axioms

## Derived fact 1 — 5 * 0 = 0

**Coordinate.** the natural numbers · multiplication · five times zero is zero · **Derived fact**

*Source: peano*

*Built on: zero is the right annihilator, for multiplication on the natural numbers*

> **Goal.** 5 * 0 = 0
>
> $$five \cdot 0 = 0$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that five times zero is zero for multiplication on the natural numbers. |  |  |
| ② | Let five = succ(succ(succ(succ(succ(0))))). |  |  |
| ③ | We invoke the definitional clause governing multiplication on the natural numbers: zero is the right annihilator, for multiplication on the natural numbers (instantiated for five). |  |  |
| ④ | From step 2 and step 3, this implies five times 0 equals 0. Hence proven. | ④ | $five \cdot 0 = 0$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`the natural numbers · multiplication · five times zero is zero`
