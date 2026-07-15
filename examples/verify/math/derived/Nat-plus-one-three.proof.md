# examples.verify.math.derived

*One plus three is four for natural numbers.*

**Source.** peano — https://en.wikipedia.org/wiki/Peano_axioms

## Derived fact 1 — 1 + 3 = 4

**Coordinate.** the natural numbers · addition · one plus three is four · **Derived fact**

*Source: peano*

*Built on: successor on the right via commutativity, for addition on the natural numbers, one plus two is three, for addition on the natural numbers*

> **Goal.** 1 + 3 = 4
>
> $$\mathrm{succ}(0) + three = \mathrm{succ}(three)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that one plus three is four for addition on the natural numbers. |  |  |
| ② | Let three = succ(succ(succ(0))). |  |  |
| ③ | We invoke the derived fact governing addition on the natural numbers: successor on the right via commutativity, for addition on the natural numbers (instantiated for succ(0), three). |  |  |
| ④ | We invoke the derived fact governing addition on the natural numbers: one plus two is three, for addition on the natural numbers. |  |  |
| ⑤ | From step 2, step 3, and step 4, this implies the successor of 0 plus three equals the successor of three. Hence proven. | ⑤ | $\mathrm{succ}(0) + three = \mathrm{succ}(three)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ⑤ | step 2, step 3, and step 4 |

`the natural numbers · addition · one plus three is four`
