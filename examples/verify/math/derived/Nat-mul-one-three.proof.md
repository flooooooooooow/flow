# examples.verify.math.derived

*One times three is three for natural numbers.*

**Source.** peano — https://en.wikipedia.org/wiki/Peano_axioms

## Derived fact 1 — 1 * 3 = 3

**Coordinate.** the natural numbers · multiplication · one times three is three · **Derived fact**

*Source: peano*

*Built on: one is the left identity, for multiplication on the natural numbers*

> **Goal.** 1 * 3 = 3
>
> $$\mathrm{succ}(0) * three = three$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that one times three is three for multiplication on the natural numbers. |  |  |
| ② | Let three = succ(succ(succ(0))). |  |  |
| ③ | We invoke the derived fact governing multiplication on the natural numbers: one is the left identity, for multiplication on the natural numbers (instantiated for three). |  |  |
| ④ | From step 2 and step 3, this implies the successor of 0 times three equals three. Hence proven. | ④ | $\mathrm{succ}(0) * three = three$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`the natural numbers · multiplication · one times three is three`
