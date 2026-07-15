# examples.verify.math.derived

*Six plus one is seven for natural numbers.*

**Source.** peano — https://en.wikipedia.org/wiki/Peano_axioms

## Derived fact 1 — 6 + 1 = 7

**Coordinate.** the natural numbers · addition · six plus one is seven · **Derived fact**

*Source: peano*

*Built on: successor on the right via commutativity, for addition on the natural numbers, adding zero on the right does not change the number*

> **Goal.** 6 + 1 = 7
>
> $$six + \mathrm{succ}(0) = \mathrm{succ}(six)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that six plus one is seven for addition on the natural numbers. |  |  |
| ② | Let six = succ(succ(succ(succ(succ(succ(0)))))). |  |  |
| ③ | We invoke the derived fact governing addition on the natural numbers: successor on the right via commutativity, for addition on the natural numbers (instantiated for six, 0). |  |  |
| ④ | We invoke the derived fact governing addition on the natural numbers: adding zero on the right does not change the number (instantiated for six). | ④ | $six + 0 = six$ |
| ⑤ | From step 2, step 3, and step 4, this implies six plus the successor of 0 equals the successor of six. Hence proven. | ⑤ | $six + \mathrm{succ}(0) = \mathrm{succ}(six)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ⑤ | step 2, step 3, and step 4 |

`the natural numbers · addition · six plus one is seven`
