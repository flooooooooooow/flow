# examples.verify.math.derived

*One plus zero is one for natural numbers.*

**Source.** peano — https://en.wikipedia.org/wiki/Peano_axioms

## Derived fact 1 — 1 + 0 = 1

**Coordinate.** the natural numbers · addition · one plus zero is one · **Derived fact**

*Source: peano*

*Built on: adding zero on the right does not change the number*

> **Goal.** 1 + 0 = 1
>
> $$\mathrm{succ}(0) + 0 = \mathrm{succ}(0)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that one plus zero is one for addition on the natural numbers. |  |  |
| ② | We invoke the derived fact governing addition on the natural numbers: adding zero on the right does not change the number (instantiated for succ(0)). | ② | $\mathrm{succ}(0) + 0 = \mathrm{succ}(0)$ |
| ③ | From step 2, this implies the successor of 0 plus 0 equals the successor of 0. Hence proven. | ③ | $\mathrm{succ}(0) + 0 = \mathrm{succ}(0)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ③ | step 2 |

`the natural numbers · addition · one plus zero is one`
