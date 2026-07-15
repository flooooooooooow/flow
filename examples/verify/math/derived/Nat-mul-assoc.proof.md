# examples.verify.math.derived

*Multiplication associates on natural numbers.*

**Source.** peano — https://en.wikipedia.org/wiki/Associative_property

## Derived fact 1 — (a * b) * c = a * (b * c)

**Coordinate.** the natural numbers · multiplication · parentheses do not matter · **Derived fact**

*Source: peano/induction — Gries & Schneider, Ch. 3*

*Built on: zero is the left annihilator, for multiplication on the natural numbers, successor on the right distributes, for multiplication on the natural numbers, distributes over addition on the right, for multiplication on the natural numbers*

> **Goal.** (a * b) * c = a * (b * c)
>
> $$\forall a \in \mathbb{N} \forall b \in \mathbb{N} \forall c \in \mathbb{N}\quad (a \cdot b) * c = a * (b \cdot c)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that parentheses do not matter for multiplication on the natural numbers. |  |  |
| ② | We proceed by induction on a: first the base case, then the inductive step. |  |  |
| ③ | Consider the base case in which a is zero. |  |  |
| ④ | We invoke the definitional clause governing multiplication on the natural numbers: zero is the left annihilator, for multiplication on the natural numbers (instantiated for b). |  |  |
| ⑤ | We invoke the definitional clause governing multiplication on the natural numbers: zero is the left annihilator, for multiplication on the natural numbers (instantiated for b * c). |  |  |
| ⑥ | From step 3, step 4, and step 5, we can deduce that (a times b) times c equals a times (b times c). This establishes the base case (see step 3, step 4, and step 5). Hence proven. | ⑥ | $(a \cdot b) * c = a * (b \cdot c)$ |
| ⑦ | For the inductive step, suppose the claim holds for all smaller values. |  |  |
| ⑧ | Under the supposition in step 7, let n denote the predecessor of a. |  |  |
| ⑨ | Under the supposition in step 7, we cross the inductive boundary: assume the claim holds for n (the induction hypothesis). | ⑨ | $(n \cdot b) * c = n * (b \cdot c)$ |
| ⑩ | We invoke the definitional clause governing multiplication on the natural numbers: successor on the right distributes, for multiplication on the natural numbers (instantiated for n, b). |  |  |
| ⑪ | We invoke the derived fact governing multiplication on the natural numbers: distributes over addition on the right, for multiplication on the natural numbers (instantiated for n, b, c). |  |  |
| ⑫ | From step 7, step 8, step 9, step 10, and step 11, this implies (a times b) times c equals a times (b times c). Hence proven. | ⑫ | $(a \cdot b) * c = a * (b \cdot c)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 3 |
| ⑤ | step 3 |
| ⑥ | step 3, step 4, and step 5 |
| ⑧ | step 7 |
| ⑨ | step 7 |
| ⑫ | step 7, step 8, step 9, step 10, and step 11 |

`the natural numbers · multiplication · parentheses do not matter`
