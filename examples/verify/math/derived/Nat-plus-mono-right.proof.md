# examples.verify.math.derived

*Adding the same term on the right preserves less-or-equal.*

**Source.** peano — https://en.wikipedia.org/wiki/Monotonic_function

## Derived fact 1 — If b ≤ c then a + b ≤ a + c

**Coordinate.** the natural numbers · addition · adding on the right preserves order · **Derived fact**

*Source: peano/induction — Gries & Schneider, Ch. 3*

*Built on: less-or-equal is reflexive, for order on the natural numbers, less-or-equal is transitive, for order on the natural numbers, adding zero on the left does not change the number*

> **Goal.** If b ≤ c then a + b ≤ a + c
>
> $$\forall a \in \mathbb{N} \forall b \in \mathbb{N} \forall c \in \mathbb{N}\quad a + b \le a + c$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that adding on the right preserves order for addition on the natural numbers. |  |  |
| ② | We proceed by induction on a: first the base case, then the inductive step. |  |  |
| ③ | Consider the base case in which b <= c. |  |  |
| ④ | Consider the base case in which a is zero. |  |  |
| ⑤ | We invoke the definitional clause governing addition on the natural numbers: adding zero on the left does not change the number (instantiated for b). | ⑤ | $0 + b = b$ |
| ⑥ | We invoke the definitional clause governing addition on the natural numbers: adding zero on the left does not change the number (instantiated for c). | ⑥ | $0 + c = c$ |
| ⑦ | From step 4, step 5, and step 6, we can deduce that a plus b is at most a plus c. This establishes the base case (see step 4, step 5, and step 6). Hence proven. | ⑦ | $a + b \le a + c$ |
| ⑧ | For the inductive step, suppose the claim holds for all smaller values. |  |  |
| ⑨ | Under the supposition in step 8, let n denote the predecessor of a. |  |  |
| ⑩ | Under the supposition in step 8, we cross the inductive boundary: assume the claim holds for n (the induction hypothesis). | ⑩ | $n + b \le n + c$ |
| ⑪ | We invoke the derived fact governing order on the natural numbers: less-or-equal is transitive, for order on the natural numbers (instantiated for n + b, c + b, c + c). |  |  |
| ⑫ | From step 8, step 9, step 10, and step 11, this implies a plus b is at most a plus c. Hence proven. | ⑫ | $a + b \le a + c$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ⑤ | step 4 |
| ⑥ | step 4 |
| ⑦ | step 4, step 5, and step 6 |
| ⑨ | step 8 |
| ⑩ | step 8 |
| ⑫ | step 8, step 9, step 10, and step 11 |

`the natural numbers · addition · adding on the right preserves order`
