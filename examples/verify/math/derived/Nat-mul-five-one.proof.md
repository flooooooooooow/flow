# examples.verify.math.derived

*Five times one is five for natural numbers.*

**Source.** peano — https://en.wikipedia.org/wiki/Peano_axioms

## Derived fact 1 — 5 * 1 = 5

**Coordinate.** the natural numbers · multiplication · five times one is five · **Derived fact**

*Source: peano*

*Built on: one is the right identity, for multiplication on the natural numbers*

> **Goal.** 5 * 1 = 5
>
> $$five * \mathrm{succ}(0) = five$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that five times one is five for multiplication on the natural numbers. |  |  |
| ② | Let five = succ(succ(succ(succ(succ(0))))). |  |  |
| ③ | We invoke the derived fact governing multiplication on the natural numbers: one is the right identity, for multiplication on the natural numbers (instantiated for five). |  |  |
| ④ | From step 2 and step 3, this implies five times the successor of 0 equals five. Hence proven. | ④ | $five * \mathrm{succ}(0) = five$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`the natural numbers · multiplication · five times one is five`
