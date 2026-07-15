# examples.verify.math.derived

*Four plus one is five for natural numbers.*

**Source.** peano — https://en.wikipedia.org/wiki/Peano_axioms

## Derived fact 1 — 4 + 1 = 5

**Coordinate.** the natural numbers · addition · four plus one is five · **Derived fact**

*Source: peano*

*Built on: successor on the right via commutativity, for addition on the natural numbers, four plus zero is four, for addition on the natural numbers*

> **Goal.** 4 + 1 = 5
>
> $$four + \mathrm{succ}(0) = \mathrm{succ}(four)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that four plus one is five for addition on the natural numbers. |  |  |
| ② | Let four = succ(succ(succ(succ(0)))). |  |  |
| ③ | We invoke the derived fact governing addition on the natural numbers: successor on the right via commutativity, for addition on the natural numbers (instantiated for four, 0). |  |  |
| ④ | We invoke the derived fact governing addition on the natural numbers: four plus zero is four, for addition on the natural numbers. |  |  |
| ⑤ | From step 2, step 3, and step 4, this implies four plus the successor of 0 equals the successor of four. Hence proven. | ⑤ | $four + \mathrm{succ}(0) = \mathrm{succ}(four)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ⑤ | step 2, step 3, and step 4 |

`the natural numbers · addition · four plus one is five`
