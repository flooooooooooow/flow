# examples.verify.math.derived

*One is the right multiplicative identity.*

**Source.** peano — https://en.wikipedia.org/wiki/Peano_axioms

## Derived fact 1 — m * succ(0) = m, i

**Coordinate.** the natural numbers · multiplication · one is the right identity · **Derived fact**

*Source: peano/induction — Gries & Schneider, Ch. 3*

*Built on: one is the left identity, for multiplication on the natural numbers, order does not matter, for multiplication on the natural numbers*

> **Goal.** m * succ(0) = m, i.e. m * 1 = m
>
> $$\forall m \in \mathbb{N}\quad m * \mathrm{succ}(0) = m$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that one is the right identity for multiplication on the natural numbers. |  |  |
| ② | We invoke the derived fact governing multiplication on the natural numbers: one is the left identity, for multiplication on the natural numbers (instantiated for succ(0)). |  |  |
| ③ | We invoke the derived fact governing multiplication on the natural numbers: order does not matter, for multiplication on the natural numbers (instantiated for m, succ(0)). |  |  |
| ④ | We invoke the derived fact governing multiplication on the natural numbers: order does not matter, for multiplication on the natural numbers (instantiated for succ(0), m). |  |  |
| ⑤ | From step 2, step 3, and step 4, this implies m times the successor of 0 equals m. Hence proven. | ⑤ | $m * \mathrm{succ}(0) = m$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ⑤ | step 2, step 3, and step 4 |

`the natural numbers · multiplication · one is the right identity`
