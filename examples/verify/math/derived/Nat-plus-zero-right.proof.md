# examples.verify.math.derived

*n + 0 = n, derived by induction.*

**Source.** peano/induction — Gries & Schneider, Ch. 3

## Derived fact 1 — Adding zero on the right gives the same number

**Coordinate.** the natural numbers · addition · zero is the right identity · **Derived fact**

*Source: peano/induction — https://en.wikipedia.org/wiki/Mathematical_induction*

*Built on: adding zero on the left does not change the number, adding one more on the right bumps the sum by one*

> **Goal.** Adding zero on the right gives the same number.  (12 + 0 = 12)
>
> $$\forall n \in \mathbb{N}\quad n + 0 = n$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that zero is the right identity for addition on the natural numbers. |  |  |
| ② | We proceed by induction on n: first the base case, then the inductive step. |  |  |
| ③ | Consider the base case in which n is zero. |  |  |
| ④ | We invoke the definitional clause governing addition on the natural numbers: adding zero on the left does not change the number (instantiated for 0). | ④ | $0 + 0 = 0$ |
| ⑤ | From step 3 and step 4, we can deduce that 0 plus 0 equals 0. This establishes the base case (see step 3 and step 4). Hence proven. | ⑤ | $0 + 0 = 0$ |
| ⑥ | For the inductive step, suppose the claim holds for all smaller values. |  |  |
| ⑦ | Under the supposition in step 6, let k denote the predecessor of n. |  |  |
| ⑧ | Under the supposition in step 6, we cross the inductive boundary: assume the claim holds for k (the induction hypothesis). | ⑧ | $k + 0 = k$ |
| ⑨ | We invoke the definitional clause governing addition on the natural numbers: adding one more on the right bumps the sum by one (instantiated for k, 0). | ⑨ | $k + \mathrm{succ}(0) = \mathrm{succ}(k + 0)$ |
| ⑩ | From step 6, step 7, step 8, and step 9, this implies n plus 0 equals n. Hence proven. | ⑩ | $n + 0 = n$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 3 |
| ⑤ | step 3 and step 4 |
| ⑦ | step 6 |
| ⑧ | step 6 |
| ⑩ | step 6, step 7, step 8, and step 9 |

`the natural numbers · addition · zero is the right identity`
