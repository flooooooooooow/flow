# examples.verify.math.derived

*One plus two is three for natural numbers.*

**Source.** peano — https://en.wikipedia.org/wiki/Peano_axioms

## Derived fact 1 — 1 + 2 = 3

**Coordinate.** the natural numbers · addition · one plus two is three · **Derived fact**

*Source: peano*

*Built on: successor on the right via commutativity, for addition on the natural numbers, one plus one is two, for addition on the natural numbers*

> **Goal.** 1 + 2 = 3
>
> $$\mathrm{succ}(0) + two = \mathrm{succ}(succ(0))$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that one plus two is three for addition on the natural numbers. |  |  |
| ② | Let two = succ(succ(0)). |  |  |
| ③ | We invoke the derived fact governing addition on the natural numbers: successor on the right via commutativity, for addition on the natural numbers (instantiated for succ(0), two). |  |  |
| ④ | We invoke the derived fact governing addition on the natural numbers: one plus one is two, for addition on the natural numbers. |  |  |
| ⑤ | From step 2, step 3, and step 4, this implies the successor of 0 plus two equals the successor of succ(0). Hence proven. | ⑤ | $\mathrm{succ}(0) + two = \mathrm{succ}(succ(0))$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ⑤ | step 2, step 3, and step 4 |

`the natural numbers · addition · one plus two is three`
