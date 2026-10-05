# examples.verify.math.derived

*Zero plus one is one for natural numbers.*

**Source.** peano — https://en.wikipedia.org/wiki/Peano_axioms

## Derived fact 1 — 0 + 1 = 1

**Coordinate.** the natural numbers · addition · zero plus one is one · **Derived fact**

*Source: peano*

*Built on: zero on the left gives the value, for addition on the natural numbers*

> **Goal.** 0 + 1 = 1
>
> $$0 + \mathrm{succ}(0) = \mathrm{succ}(0)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that zero plus one is one for addition on the natural numbers. |  |  |
| ② | We invoke the derived fact governing addition on the natural numbers: zero on the left gives the value, for addition on the natural numbers (instantiated for succ(0)). |  |  |
| ③ | From step 2, this implies 0 plus the successor of 0 equals the successor of 0. Hence proven. | ③ | $0 + \mathrm{succ}(0) = \mathrm{succ}(0)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ③ | step 2 |

`the natural numbers · addition · zero plus one is one`
