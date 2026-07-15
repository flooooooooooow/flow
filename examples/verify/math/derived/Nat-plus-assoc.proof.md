# examples.verify.math.derived

*Addition associates: parentheses on the left can move to the right.*

**Source.** landau — *Foundations of Analysis*, Ch. 1

## Derived fact 1 — (a + b) + c = a + (b + c)

**Coordinate.** the natural numbers · addition · parentheses do not matter · **Derived fact**

*Source: peano/induction — Gries & Schneider, Ch. 3*

*Built on: adding zero on the left does not change the number, successor on the left steps the sum, for addition on the natural numbers*

> **Goal.** (a + b) + c = a + (b + c)
>
> $$\forall a \in \mathbb{N} \forall b \in \mathbb{N} \forall c \in \mathbb{N}\quad (a + b) + c = a + (b + c)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that parentheses do not matter for addition on the natural numbers. |  |  |
| ② | We proceed by induction on a: first the base case, then the inductive step. |  |  |
| ③ | Consider the base case in which a is zero. |  |  |
| ④ | We invoke the definitional clause governing addition on the natural numbers: adding zero on the left does not change the number (instantiated for b). | ④ | $0 + b = b$ |
| ⑤ | We invoke the definitional clause governing addition on the natural numbers: adding zero on the left does not change the number (instantiated for b + c). | ⑤ | $0 + b + c = b + c$ |
| ⑥ | From step 3, step 4, and step 5, we can deduce that (a plus b) plus c equals a plus (b plus c). This establishes the base case (see step 3, step 4, and step 5). Hence proven. | ⑥ | $(a + b) + c = a + (b + c)$ |
| ⑦ | For the inductive step, suppose the claim holds for all smaller values. |  |  |
| ⑧ | Under the supposition in step 7, let n denote the predecessor of a. |  |  |
| ⑨ | Under the supposition in step 7, we cross the inductive boundary: assume the claim holds for n (the induction hypothesis). | ⑨ | $(n + b) + c = n + (b + c)$ |
| ⑩ | We invoke the derived fact governing addition on the natural numbers: successor on the left steps the sum, for addition on the natural numbers (instantiated for n, b). |  |  |
| ⑪ | We invoke the derived fact governing addition on the natural numbers: successor on the left steps the sum, for addition on the natural numbers (instantiated for n, b + c). |  |  |
| ⑫ | From step 7, step 8, step 9, step 10, and step 11, this implies (a plus b) plus c equals a plus (b plus c). Hence proven. | ⑫ | $(a + b) + c = a + (b + c)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 3 |
| ⑤ | step 3 |
| ⑥ | step 3, step 4, and step 5 |
| ⑧ | step 7 |
| ⑨ | step 7 |
| ⑫ | step 7, step 8, step 9, step 10, and step 11 |

`the natural numbers · addition · parentheses do not matter`
