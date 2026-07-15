# examples.verify.math.derived

*One is less than or equal to itself.*

**Source.** peano — https://en.wikipedia.org/wiki/Total_order

## Derived fact 1 — 1 <= 1

**Coordinate.** the natural numbers · order · one is below itself · **Derived fact**

*Source: peano*

*Built on: less-or-equal is reflexive, for order on the natural numbers*

> **Goal.** 1 <= 1
>
> $$\mathrm{succ}(0) \le \mathrm{succ}(0)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that one is below itself for order on the natural numbers. |  |  |
| ② | We invoke the derived fact governing order on the natural numbers: less-or-equal is reflexive, for order on the natural numbers (instantiated for succ(0)). |  |  |
| ③ | From step 2, this implies the successor of 0 is at most the successor of 0. Hence proven. | ③ | $\mathrm{succ}(0) \le \mathrm{succ}(0)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ③ | step 2 |

`the natural numbers · order · one is below itself`
