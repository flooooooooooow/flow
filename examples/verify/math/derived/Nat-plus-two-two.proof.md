# examples.verify.math.derived

*Two plus two is four for natural numbers.*

**Source.** peano — https://en.wikipedia.org/wiki/Peano_axioms

## Derived fact 1 — 2 + 2 = 4

**Coordinate.** the natural numbers · addition · two plus two is four · **Derived fact**

*Source: peano*

*Built on: successor on the right via commutativity, for addition on the natural numbers, two plus one is three, for addition on the natural numbers*

> **Goal.** 2 + 2 = 4
>
> $$two + two = \mathrm{succ}(three)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that two plus two is four for addition on the natural numbers. |  |  |
| ② | Let two = succ(succ(0)). |  |  |
| ③ | Let three = succ(two). |  |  |
| ④ | We invoke the derived fact governing addition on the natural numbers: successor on the right via commutativity, for addition on the natural numbers (instantiated for two, two). |  |  |
| ⑤ | We invoke the derived fact governing addition on the natural numbers: two plus one is three, for addition on the natural numbers. |  |  |
| ⑥ | From step 2, step 3, step 4, and step 5, this implies two plus two equals the successor of three. Hence proven. | ⑥ | $two + two = \mathrm{succ}(three)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ⑥ | step 2, step 3, step 4, and step 5 |

`the natural numbers · addition · two plus two is four`
