# examples.verify.math.derived

*Five plus one is six for natural numbers.*

**Source.** peano — https://en.wikipedia.org/wiki/Peano_axioms

## Derived fact 1 — 5 + 1 = 6

**Coordinate.** the natural numbers · addition · five plus one is six · **Derived fact**

*Source: peano*

*Built on: successor on the right via commutativity, for addition on the natural numbers, adding zero on the right does not change the number*

> **Goal.** 5 + 1 = 6
>
> $$five + \mathrm{succ}(0) = \mathrm{succ}(five)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that five plus one is six for addition on the natural numbers. |  |  |
| ② | Let five = succ(succ(succ(succ(succ(0))))). |  |  |
| ③ | We invoke the derived fact governing addition on the natural numbers: successor on the right via commutativity, for addition on the natural numbers (instantiated for five, 0). |  |  |
| ④ | We invoke the derived fact governing addition on the natural numbers: adding zero on the right does not change the number (instantiated for five). | ④ | $five + 0 = five$ |
| ⑤ | From step 2, step 3, and step 4, this implies five plus the successor of 0 equals the successor of five. Hence proven. | ⑤ | $five + \mathrm{succ}(0) = \mathrm{succ}(five)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ⑤ | step 2, step 3, and step 4 |

`the natural numbers · addition · five plus one is six`
