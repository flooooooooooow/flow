# examples.verify.math.derived

*Two times one is two for natural numbers.*

**Source.** peano — https://en.wikipedia.org/wiki/Peano_axioms

## Derived fact 1 — 2 * 1 = 2

**Coordinate.** the natural numbers · multiplication · two times one is two · **Derived fact**

*Source: peano*

*Built on: one is the right identity, for multiplication on the natural numbers*

> **Goal.** 2 * 1 = 2
>
> $$two * \mathrm{succ}(0) = two$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that two times one is two for multiplication on the natural numbers. |  |  |
| ② | Let two = succ(succ(0)). |  |  |
| ③ | We invoke the derived fact governing multiplication on the natural numbers: one is the right identity, for multiplication on the natural numbers (instantiated for two). |  |  |
| ④ | From step 2 and step 3, this implies two times the successor of 0 equals two. Hence proven. | ④ | $two * \mathrm{succ}(0) = two$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`the natural numbers · multiplication · two times one is two`
