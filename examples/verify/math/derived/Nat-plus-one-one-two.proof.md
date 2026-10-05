# examples.verify.math.derived

*One plus one is two for natural numbers.*

**Source.** peano — https://en.wikipedia.org/wiki/Peano_axioms

## Derived fact 1 — 1 + 1 = 2

**Coordinate.** the natural numbers · addition · one plus one is two · **Derived fact**

*Source: peano*

*Built on: successor on the right via commutativity, for addition on the natural numbers, one plus zero is one, for addition on the natural numbers*

> **Goal.** 1 + 1 = 2
>
> $$\mathrm{succ}(0) + \mathrm{succ}(0) = \mathrm{succ}(succ(0))$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that one plus one is two for addition on the natural numbers. |  |  |
| ② | We invoke the derived fact governing addition on the natural numbers: successor on the right via commutativity, for addition on the natural numbers (instantiated for succ(0), 0). |  |  |
| ③ | We invoke the derived fact governing addition on the natural numbers: one plus zero is one, for addition on the natural numbers. |  |  |
| ④ | From step 2 and step 3, this implies the successor of 0 plus the successor of 0 equals the successor of succ(0). Hence proven. | ④ | $\mathrm{succ}(0) + \mathrm{succ}(0) = \mathrm{succ}(succ(0))$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`the natural numbers · addition · one plus one is two`
