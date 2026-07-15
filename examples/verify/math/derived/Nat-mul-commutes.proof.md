# examples.verify.math.derived

*Multiplication commutes on natural numbers.*

**Source.** peano — https://en.wikipedia.org/wiki/Peano_axioms

## Derived fact 1 — a * b = b * a

**Coordinate.** the natural numbers · multiplication · order does not matter · **Derived fact**

*Source: peano/induction — Gries & Schneider, Ch. 3*

*Built on: zero is the left annihilator, for multiplication on the natural numbers, zero is the right annihilator, for multiplication on the natural numbers, successor on the right distributes, for multiplication on the natural numbers, you can swap the order when you add*

> **Goal.** a * b = b * a
>
> $$\forall a \in \mathbb{N} \forall b \in \mathbb{N}\quad a \cdot b = b \cdot a$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that order does not matter for multiplication on the natural numbers. |  |  |
| ② | We proceed by induction on a: first the base case, then the inductive step. |  |  |
| ③ | Consider the base case in which b is zero. |  |  |
| ④ | We invoke the definitional clause governing multiplication on the natural numbers: zero is the right annihilator, for multiplication on the natural numbers (instantiated for a). |  |  |
| ⑤ | We invoke the definitional clause governing multiplication on the natural numbers: zero is the left annihilator, for multiplication on the natural numbers (instantiated for a). |  |  |
| ⑥ | From step 3, step 4, and step 5, we can deduce that a times b equals b times a. This establishes the base case (see step 3, step 4, and step 5). Hence proven. | ⑥ | $a \cdot b = b \cdot a$ |
| ⑦ | For the inductive step, suppose the claim holds for all smaller values. |  |  |
| ⑧ | Under the supposition in step 7, let k denote the predecessor of b. |  |  |
| ⑨ | Under the supposition in step 7, we cross the inductive boundary: assume the claim holds for a (the induction hypothesis). | ⑨ | $a \cdot k = k \cdot a$ |
| ⑩ | We invoke the definitional clause governing multiplication on the natural numbers: successor on the right distributes, for multiplication on the natural numbers (instantiated for a, k). |  |  |
| ⑪ | We invoke the derived fact governing addition on the natural numbers: you can swap the order when you add (instantiated for a, k). | ⑪ | $a + k = k + a$ |
| ⑫ | We invoke the derived fact governing addition on the natural numbers: you can swap the order when you add (instantiated for k, a). | ⑫ | $k + a = a + k$ |
| ⑬ | From step 7, step 8, step 9, step 10, step 11, and step 12, this implies a times b equals b times a. Hence proven. | ⑬ | $a \cdot b = b \cdot a$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 3 |
| ⑤ | step 3 |
| ⑥ | step 3, step 4, and step 5 |
| ⑧ | step 7 |
| ⑨ | step 7 |
| ⑬ | step 7, step 8, step 9, step 10, step 11, and step 12 |

`the natural numbers · multiplication · order does not matter`
