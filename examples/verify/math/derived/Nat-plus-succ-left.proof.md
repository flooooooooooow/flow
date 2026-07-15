# examples.verify.math.derived

*Adding a successor on the left steps the sum by one.*

**Source.** peano — https://en.wikipedia.org/wiki/Peano_axioms

## Derived fact 1 — succ(a) + b = succ(a + b)

**Coordinate.** the natural numbers · addition · successor on the left steps the sum · **Derived fact**

*Source: peano/induction — Gries & Schneider, Ch. 3*

*Built on: adding zero on the left does not change the number, adding zero on the right does not change the number, you can swap the order when you add, adding one more on the right bumps the sum by one*

> **Goal.** succ(a) + b = succ(a + b)
>
> $$\forall a \in \mathbb{N} \forall b \in \mathbb{N}\quad \mathrm{succ}(a) + b = \mathrm{succ}(a + b)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that successor on the left steps the sum for addition on the natural numbers. |  |  |
| ② | We proceed by induction on a: first the base case, then the inductive step. |  |  |
| ③ | Consider the base case in which a is zero. |  |  |
| ④ | We invoke the definitional clause governing addition on the natural numbers: adding zero on the left does not change the number (instantiated for b). | ④ | $0 + b = b$ |
| ⑤ | We invoke the derived fact governing addition on the natural numbers: you can swap the order when you add (instantiated for 0, b). | ⑤ | $0 + b = b + 0$ |
| ⑥ | We invoke the definitional clause governing addition on the natural numbers: adding one more on the right bumps the sum by one (instantiated for b, 0). | ⑥ | $b + \mathrm{succ}(0) = \mathrm{succ}(b + 0)$ |
| ⑦ | We invoke the derived fact governing addition on the natural numbers: adding zero on the right does not change the number (instantiated for b). | ⑦ | $b + 0 = b$ |
| ⑧ | From step 3, step 4, step 5, step 6, and step 7, we can deduce that the successor of a plus b equals the successor of a plus b. This establishes the base case (see step 3, step 4, step 5, step 6, and step 7). Hence proven. | ⑧ | $\mathrm{succ}(a) + b = \mathrm{succ}(a + b)$ |
| ⑨ | For the inductive step, suppose the claim holds for all smaller values. |  |  |
| ⑩ | Under the supposition in step 9, let n denote the predecessor of a. |  |  |
| ⑪ | Under the supposition in step 9, we cross the inductive boundary: assume the claim holds for n (the induction hypothesis). | ⑪ | $\mathrm{succ}(n) + b = \mathrm{succ}(n + b)$ |
| ⑫ | We invoke the derived fact governing addition on the natural numbers: you can swap the order when you add (instantiated for succ(n), b). | ⑫ | $\mathrm{succ}(n) + b = b + \mathrm{succ}(n)$ |
| ⑬ | We invoke the derived fact governing addition on the natural numbers: you can swap the order when you add (instantiated for n, b). | ⑬ | $n + b = b + n$ |
| ⑭ | We invoke the definitional clause governing addition on the natural numbers: adding one more on the right bumps the sum by one (instantiated for n, b). | ⑭ | $n + \mathrm{succ}(b) = \mathrm{succ}(n + b)$ |
| ⑮ | From step 9, step 10, step 11, step 12, step 13, and step 14, this implies the successor of a plus b equals the successor of a plus b. Hence proven. | ⑮ | $\mathrm{succ}(a) + b = \mathrm{succ}(a + b)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 3 |
| ⑤ | step 3 |
| ⑥ | step 3 |
| ⑦ | step 3 |
| ⑧ | step 3, step 4, step 5, step 6, and step 7 |
| ⑩ | step 9 |
| ⑪ | step 9 |
| ⑮ | step 9, step 10, step 11, step 12, step 13, and step 14 |

`the natural numbers · addition · successor on the left steps the sum`
