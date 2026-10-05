# examples.verify.math.derived

*Two plus zero is two for natural numbers.*

**Source.** peano — https://en.wikipedia.org/wiki/Peano_axioms

## Derived fact 1 — 2 + 0 = 2

**Coordinate.** the natural numbers · addition · two plus zero is two · **Derived fact**

*Source: peano*

*Built on: adding zero on the right does not change the number*

> **Goal.** 2 + 0 = 2
>
> $$two + 0 = two$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that two plus zero is two for addition on the natural numbers. |  |  |
| ② | Let two = succ(succ(0)). |  |  |
| ③ | We invoke the derived fact governing addition on the natural numbers: adding zero on the right does not change the number (instantiated for two). | ③ | $two + 0 = two$ |
| ④ | From step 2 and step 3, this implies two plus 0 equals two. Hence proven. | ④ | $two + 0 = two$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`the natural numbers · addition · two plus zero is two`
