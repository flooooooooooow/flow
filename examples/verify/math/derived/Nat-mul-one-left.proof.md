# examples.verify.math.derived

*One is the left multiplicative identity.*

**Source.** peano — https://en.wikipedia.org/wiki/Peano_axioms

## Derived fact 1 — succ(0) * m = m, i

**Coordinate.** the natural numbers · multiplication · one is the left identity · **Derived fact**

*Source: peano/induction — Gries & Schneider, Ch. 3*

*Built on: zero is the right annihilator, for multiplication on the natural numbers, successor on the right distributes, for multiplication on the natural numbers, adding zero on the left does not change the number, successor on the left steps the sum, for addition on the natural numbers*

> **Goal.** succ(0) * m = m, i.e. 1 * m = m
>
> $$\forall m \in \mathbb{N}\quad \mathrm{succ}(0) * m = m$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that one is the left identity for multiplication on the natural numbers. |  |  |
| ② | We proceed by induction on m: first the base case, then the inductive step. |  |  |
| ③ | Consider the base case in which m is zero. |  |  |
| ④ | We invoke the definitional clause governing multiplication on the natural numbers: zero is the right annihilator, for multiplication on the natural numbers (instantiated for succ(0)). |  |  |
| ⑤ | We invoke the definitional clause governing addition on the natural numbers: adding zero on the left does not change the number (instantiated for 0). | ⑤ | $0 + 0 = 0$ |
| ⑥ | From step 3, step 4, and step 5, we can deduce that the successor of 0 times m equals m. This establishes the base case (see step 3, step 4, and step 5). Hence proven. | ⑥ | $\mathrm{succ}(0) * m = m$ |
| ⑦ | For the inductive step, suppose the claim holds for all smaller values. |  |  |
| ⑧ | Under the supposition in step 7, let k denote the predecessor of m. |  |  |
| ⑨ | Under the supposition in step 7, we cross the inductive boundary: assume the claim holds for k (the induction hypothesis). | ⑨ | $\mathrm{succ}(0) * k = k$ |
| ⑩ | We invoke the definitional clause governing multiplication on the natural numbers: successor on the right distributes, for multiplication on the natural numbers (instantiated for succ(0), k). |  |  |
| ⑪ | We invoke the derived fact governing addition on the natural numbers: successor on the left steps the sum, for addition on the natural numbers (instantiated for 0, k). |  |  |
| ⑫ | We invoke the definitional clause governing addition on the natural numbers: adding zero on the left does not change the number (instantiated for k). | ⑫ | $0 + k = k$ |
| ⑬ | From step 7, step 8, step 9, step 10, step 11, and step 12, this implies the successor of 0 times m equals m. Hence proven. | ⑬ | $\mathrm{succ}(0) * m = m$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 3 |
| ⑤ | step 3 |
| ⑥ | step 3, step 4, and step 5 |
| ⑧ | step 7 |
| ⑨ | step 7 |
| ⑬ | step 7, step 8, step 9, step 10, step 11, and step 12 |

`the natural numbers · multiplication · one is the left identity`
