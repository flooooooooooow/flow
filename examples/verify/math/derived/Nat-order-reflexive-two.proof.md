# examples.verify.math.derived

*Two is less than or equal to itself.*

**Source.** peano — https://en.wikipedia.org/wiki/Total_order

## Derived fact 1 — 2 <= 2

**Coordinate.** the natural numbers · order · two is below itself · **Derived fact**

*Source: peano*

*Built on: less-or-equal is reflexive, for order on the natural numbers*

> **Goal.** 2 <= 2
>
> $$two \le two$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that two is below itself for order on the natural numbers. |  |  |
| ② | Let two = succ(succ(0)). |  |  |
| ③ | We invoke the derived fact governing order on the natural numbers: less-or-equal is reflexive, for order on the natural numbers (instantiated for two). |  |  |
| ④ | From step 2 and step 3, this implies two is at most two. Hence proven. | ④ | $two \le two$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`the natural numbers · order · two is below itself`
