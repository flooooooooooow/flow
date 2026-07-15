# examples.verify.math.derived

*Multiplication distributes over addition on the right.*

**Source.** peano — https://en.wikipedia.org/wiki/Distributive_property

## Derived fact 1 — a * (b + c) = a * b + a * c

**Coordinate.** the natural numbers · multiplication · distributes over addition on the right · **Derived fact**

*Source: peano/induction — Gries & Schneider, Ch. 3*

*Built on: zero is the right annihilator, for multiplication on the natural numbers, successor on the right distributes, for multiplication on the natural numbers, adding one more on the right bumps the sum by one*

> **Goal.** a * (b + c) = a * b + a * c
>
> $$\forall a \in \mathbb{N} \forall b \in \mathbb{N} \forall c \in \mathbb{N}\quad a * (b + c) = a \cdot b + a \cdot c$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that distributes over addition on the right for multiplication on the natural numbers. |  |  |
| ② | We proceed by induction on a: first the base case, then the inductive step. |  |  |
| ③ | Consider the base case in which b is zero. |  |  |
| ④ | We invoke the definitional clause governing multiplication on the natural numbers: zero is the right annihilator, for multiplication on the natural numbers (instantiated for a). |  |  |
| ⑤ | We invoke the definitional clause governing multiplication on the natural numbers: zero is the right annihilator, for multiplication on the natural numbers (instantiated for a). |  |  |
| ⑥ | We invoke the definitional clause governing addition on the natural numbers: adding zero on the left does not change the number (instantiated for c). | ⑥ | $0 + c = c$ |
| ⑦ | From step 3, step 4, step 5, and step 6, we can deduce that a times (b plus c) equals a times b plus a times c. This establishes the base case (see step 3, step 4, step 5, and step 6). Hence proven. | ⑦ | $a * (b + c) = a \cdot b + a \cdot c$ |
| ⑧ | For the inductive step, suppose the claim holds for all smaller values. |  |  |
| ⑨ | Under the supposition in step 8, let k denote the predecessor of b. |  |  |
| ⑩ | Under the supposition in step 8, we cross the inductive boundary: assume the claim holds for a (the induction hypothesis). | ⑩ | $a * (k + c) = a \cdot k + a \cdot c$ |
| ⑪ | We invoke the definitional clause governing multiplication on the natural numbers: successor on the right distributes, for multiplication on the natural numbers (instantiated for a, k). |  |  |
| ⑫ | We invoke the definitional clause governing addition on the natural numbers: adding one more on the right bumps the sum by one (instantiated for k, c). | ⑫ | $k + \mathrm{succ}(c) = \mathrm{succ}(k + c)$ |
| ⑬ | From step 8, step 9, step 10, step 11, and step 12, this implies a times (b plus c) equals a times b plus a times c. Hence proven. | ⑬ | $a * (b + c) = a \cdot b + a \cdot c$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 3 |
| ⑤ | step 3 |
| ⑥ | step 3 |
| ⑦ | step 3, step 4, step 5, and step 6 |
| ⑨ | step 8 |
| ⑩ | step 8 |
| ⑬ | step 8, step 9, step 10, step 11, and step 12 |

`the natural numbers · multiplication · distributes over addition on the right`
