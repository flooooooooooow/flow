# examples.verify.math.derived

*Equal factors stay equal when multiplied on the right.*

**Source.** leibniz — https://en.wikipedia.org/wiki/Substitution_(logic)

## Derived fact 1 — From a = b we deduce a * c = b * c

**Coordinate.** equality · equality · equal terms multiply the same on the right · **Derived fact**

*Source: peano/induction — Gries & Schneider, Ch. 3*

*Built on: zero is the right annihilator, for multiplication on the natural numbers, successor on the right distributes, for multiplication on the natural numbers*

> **Goal.** From a = b we deduce a * c = b * c
>
> $$\forall a \in \mathbb{N} \forall b \in \mathbb{N} \forall c \in \mathbb{N}\quad a \cdot c = b \cdot c$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that equal terms multiply the same on the right for equality on equality. |  |  |
| ② | We proceed by induction on a: first the base case, then the inductive step. |  |  |
| ③ | Consider the base case in which a  equals  b. |  |  |
| ④ | Consider the base case in which c is zero. |  |  |
| ⑤ | We invoke the definitional clause governing multiplication on the natural numbers: zero is the right annihilator, for multiplication on the natural numbers (instantiated for a). |  |  |
| ⑥ | We invoke the definitional clause governing multiplication on the natural numbers: zero is the right annihilator, for multiplication on the natural numbers (instantiated for b). |  |  |
| ⑦ | From step 4, step 5, and step 6, we can deduce that a times c equals b times c. This establishes the base case (see step 4, step 5, and step 6). Hence proven. | ⑦ | $a \cdot c = b \cdot c$ |
| ⑧ | For the inductive step, suppose the claim holds for all smaller values. |  |  |
| ⑨ | Under the supposition in step 8, let k denote the predecessor of c. |  |  |
| ⑩ | Under the supposition in step 8, we cross the inductive boundary: assume the claim holds for a (the induction hypothesis). | ⑩ | $a \cdot k = b \cdot k$ |
| ⑪ | We invoke the definitional clause governing multiplication on the natural numbers: successor on the right distributes, for multiplication on the natural numbers (instantiated for a, k). |  |  |
| ⑫ | We invoke the definitional clause governing multiplication on the natural numbers: successor on the right distributes, for multiplication on the natural numbers (instantiated for b, k). |  |  |
| ⑬ | From step 8, step 9, step 10, step 11, and step 12, this implies a times c equals b times c. Hence proven. | ⑬ | $a \cdot c = b \cdot c$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ⑤ | step 4 |
| ⑥ | step 4 |
| ⑦ | step 4, step 5, and step 6 |
| ⑨ | step 8 |
| ⑩ | step 8 |
| ⑬ | step 8, step 9, step 10, step 11, and step 12 |

`equality · equality · equal terms multiply the same on the right`
