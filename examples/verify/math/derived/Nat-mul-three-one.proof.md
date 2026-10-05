# examples.verify.math.derived

*Three times one is three for natural numbers.*

**Source.** peano — https://en.wikipedia.org/wiki/Peano_axioms

## Derived fact 1 — 3 * 1 = 3

**Coordinate.** the natural numbers · multiplication · three times one is three · **Derived fact**

*Source: peano*

*Built on: one is the right identity, for multiplication on the natural numbers*

> **Goal.** 3 * 1 = 3
>
> $$three * \mathrm{succ}(0) = three$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that three times one is three for multiplication on the natural numbers. |  |  |
| ② | Let three = succ(succ(succ(0))). |  |  |
| ③ | We invoke the derived fact governing multiplication on the natural numbers: one is the right identity, for multiplication on the natural numbers (instantiated for three). |  |  |
| ④ | From step 2 and step 3, this implies three times the successor of 0 equals three. Hence proven. | ④ | $three * \mathrm{succ}(0) = three$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`the natural numbers · multiplication · three times one is three`
