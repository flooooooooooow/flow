# examples.verify.math.derived

*Equal left summands can be cancelled from both sides of an equation.*

**Source.** peano — https://en.wikipedia.org/wiki/Cancellation_property

## Derived fact 1 — From a + b = a + c we deduce b = c

**Coordinate.** the natural numbers · addition · left cancellation holds · **Derived fact**

*Source: peano/induction — Gries & Schneider, Ch. 3*

*Built on: adding zero on the left does not change the number, successor on the left steps the sum, for addition on the natural numbers, successor is injective, for successor on the natural numbers*

> **Goal.** From a + b = a + c we deduce b = c
>
> $$\forall a \in \mathbb{N} \forall b \in \mathbb{N} \forall c \in \mathbb{N}\quad b = c$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that left cancellation holds for addition on the natural numbers. |  |  |
| ② | We proceed by induction on a: first the base case, then the inductive step. |  |  |
| ③ | Consider the base case in which a + b  equals  a + c. |  |  |
| ④ | Consider the base case in which a is zero. |  |  |
| ⑤ | We invoke the definitional clause governing addition on the natural numbers: adding zero on the left does not change the number (instantiated for b). | ⑤ | $0 + b = b$ |
| ⑥ | We invoke the definitional clause governing addition on the natural numbers: adding zero on the left does not change the number (instantiated for c). | ⑥ | $0 + c = c$ |
| ⑦ | From step 4, step 5, and step 6, we can deduce that b equals c. This establishes the base case (see step 4, step 5, and step 6). Hence proven. | ⑦ | $b = c$ |
| ⑧ | For the inductive step, suppose the claim holds for all smaller values. |  |  |
| ⑨ | Under the supposition in step 8, let n denote the predecessor of a. |  |  |
| ⑩ | We invoke the derived fact governing addition on the natural numbers: successor on the left steps the sum, for addition on the natural numbers (instantiated for n, b). |  |  |
| ⑪ | We invoke the derived fact governing addition on the natural numbers: successor on the left steps the sum, for addition on the natural numbers (instantiated for n, c). |  |  |
| ⑫ | We invoke the derived fact governing successor on the natural numbers: successor is injective, for successor on the natural numbers (instantiated for n + b, n + c). |  |  |
| ⑬ | Under the supposition in step 8, we cross the inductive boundary: assume the claim holds for n (the induction hypothesis). | ⑬ | $b = c$ |
| ⑭ | From step 8, step 9, step 10, step 11, step 12, and step 13, this implies b equals c. Hence proven. | ⑭ | $b = c$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ⑤ | step 4 |
| ⑥ | step 4 |
| ⑦ | step 4, step 5, and step 6 |
| ⑨ | step 8 |
| ⑬ | step 8 |
| ⑭ | step 8, step 9, step 10, step 11, step 12, and step 13 |

`the natural numbers · addition · left cancellation holds`
