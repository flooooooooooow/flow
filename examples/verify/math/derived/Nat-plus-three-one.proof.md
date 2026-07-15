# examples.verify.math.derived

*Three plus one is four for natural numbers.*

**Source.** peano — https://en.wikipedia.org/wiki/Peano_axioms

## Derived fact 1 — 3 + 1 = 4

**Coordinate.** the natural numbers · addition · three plus one is four · **Derived fact**

*Source: peano*

*Built on: successor on the right via commutativity, for addition on the natural numbers, three plus zero is three, for addition on the natural numbers*

> **Goal.** 3 + 1 = 4
>
> $$three + \mathrm{succ}(0) = \mathrm{succ}(three)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that three plus one is four for addition on the natural numbers. |  |  |
| ② | Let three = succ(succ(succ(0))). |  |  |
| ③ | We invoke the derived fact governing addition on the natural numbers: successor on the right via commutativity, for addition on the natural numbers (instantiated for three, 0). |  |  |
| ④ | We invoke the derived fact governing addition on the natural numbers: three plus zero is three, for addition on the natural numbers. |  |  |
| ⑤ | From step 2, step 3, and step 4, this implies three plus the successor of 0 equals the successor of three. Hence proven. | ⑤ | $three + \mathrm{succ}(0) = \mathrm{succ}(three)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ⑤ | step 2, step 3, and step 4 |

`the natural numbers · addition · three plus one is four`
