# examples.verify.math.derived

*One times two is two for natural numbers.*

**Source.** peano — https://en.wikipedia.org/wiki/Peano_axioms

## Derived fact 1 — 1 * 2 = 2

**Coordinate.** the natural numbers · multiplication · one times two is two · **Derived fact**

*Source: peano*

*Built on: one is the left identity, for multiplication on the natural numbers*

> **Goal.** 1 * 2 = 2
>
> $$\mathrm{succ}(0) * two = two$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that one times two is two for multiplication on the natural numbers. |  |  |
| ② | Let two = succ(succ(0)). |  |  |
| ③ | We invoke the derived fact governing multiplication on the natural numbers: one is the left identity, for multiplication on the natural numbers (instantiated for two). |  |  |
| ④ | From step 2 and step 3, this implies the successor of 0 times two equals two. Hence proven. | ④ | $\mathrm{succ}(0) * two = two$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`the natural numbers · multiplication · one times two is two`
