# examples.verify.math.derived

*Two plus one is three for natural numbers.*

**Source.** peano — https://en.wikipedia.org/wiki/Peano_axioms

## Derived fact 1 — 2 + 1 = 3

**Coordinate.** the natural numbers · addition · two plus one is three · **Derived fact**

*Source: peano*

*Built on: successor on the right via commutativity, for addition on the natural numbers, two plus zero is two, for addition on the natural numbers*

> **Goal.** 2 + 1 = 3
>
> $$two + \mathrm{succ}(0) = \mathrm{succ}(two)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that two plus one is three for addition on the natural numbers. |  |  |
| ② | Let two = succ(succ(0)). |  |  |
| ③ | We invoke the derived fact governing addition on the natural numbers: successor on the right via commutativity, for addition on the natural numbers (instantiated for two, 0). |  |  |
| ④ | We invoke the derived fact governing addition on the natural numbers: two plus zero is two, for addition on the natural numbers. |  |  |
| ⑤ | From step 2, step 3, and step 4, this implies two plus the successor of 0 equals the successor of two. Hence proven. | ⑤ | $two + \mathrm{succ}(0) = \mathrm{succ}(two)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ⑤ | step 2, step 3, and step 4 |

`the natural numbers · addition · two plus one is three`
