# examples.verify.math.derived

*One times one is one for natural numbers.*

**Source.** peano — https://en.wikipedia.org/wiki/Peano_axioms

## Derived fact 1 — 1 * 1 = 1, i

**Coordinate.** the natural numbers · multiplication · one times one is one · **Derived fact**

*Source: peano*

*Built on: one is the left identity, for multiplication on the natural numbers*

> **Goal.** 1 * 1 = 1, i.e. succ(0) * succ(0) = succ(0)
>
> $$\mathrm{succ}(0) * \mathrm{succ}(0) = \mathrm{succ}(0)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that one times one is one for multiplication on the natural numbers. |  |  |
| ② | We invoke the derived fact governing multiplication on the natural numbers: one is the left identity, for multiplication on the natural numbers (instantiated for succ(0)). |  |  |
| ③ | From step 2, this implies the successor of 0 times the successor of 0 equals the successor of 0. Hence proven. | ③ | $\mathrm{succ}(0) * \mathrm{succ}(0) = \mathrm{succ}(0)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ③ | step 2 |

`the natural numbers · multiplication · one times one is one`
