# examples.verify.math.derived

*Six times one is six for natural numbers.*

**Source.** peano — https://en.wikipedia.org/wiki/Peano_axioms

## Derived fact 1 — 6 * 1 = 6

**Coordinate.** the natural numbers · multiplication · six times one is six · **Derived fact**

*Source: peano*

*Built on: one is the right identity, for multiplication on the natural numbers*

> **Goal.** 6 * 1 = 6
>
> $$six * \mathrm{succ}(0) = six$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that six times one is six for multiplication on the natural numbers. |  |  |
| ② | Let six = succ(succ(succ(succ(succ(succ(0)))))). |  |  |
| ③ | We invoke the derived fact governing multiplication on the natural numbers: one is the right identity, for multiplication on the natural numbers (instantiated for six). |  |  |
| ④ | From step 2 and step 3, this implies six times the successor of 0 equals six. Hence proven. | ④ | $six * \mathrm{succ}(0) = six$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`the natural numbers · multiplication · six times one is six`
