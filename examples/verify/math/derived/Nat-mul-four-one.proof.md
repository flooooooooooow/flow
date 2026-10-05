# examples.verify.math.derived

*Four times one is four for natural numbers.*

**Source.** peano — https://en.wikipedia.org/wiki/Peano_axioms

## Derived fact 1 — 4 * 1 = 4

**Coordinate.** the natural numbers · multiplication · four times one is four · **Derived fact**

*Source: peano*

*Built on: one is the right identity, for multiplication on the natural numbers*

> **Goal.** 4 * 1 = 4
>
> $$four * \mathrm{succ}(0) = four$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that four times one is four for multiplication on the natural numbers. |  |  |
| ② | Let four = succ(succ(succ(succ(0)))). |  |  |
| ③ | We invoke the derived fact governing multiplication on the natural numbers: one is the right identity, for multiplication on the natural numbers (instantiated for four). |  |  |
| ④ | From step 2 and step 3, this implies four times the successor of 0 equals four. Hence proven. | ④ | $four * \mathrm{succ}(0) = four$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`the natural numbers · multiplication · four times one is four`
