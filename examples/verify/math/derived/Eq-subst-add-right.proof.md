# examples.verify.math.derived

*Equal summands stay equal when the same term is added on the right.*

**Source.** leibniz — https://en.wikipedia.org/wiki/Substitution_(logic)

## Derived fact 1 — From a = b we deduce a + c = b + c, by induction on c

**Coordinate.** equality · equality · equal terms add the same on the right · **Derived fact**

*Source: peano/induction — Gries & Schneider, Ch. 3*

*Built on: adding zero on the right does not change the number, adding one more on the right bumps the sum by one*

> **Goal.** From a = b we deduce a + c = b + c, by induction on c
>
> $$\forall a \in \mathbb{N} \forall b \in \mathbb{N} \forall c \in \mathbb{N}\quad a + c = b + c$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that equal terms add the same on the right for equality on equality. |  |  |
| ② | We proceed by induction on a: first the base case, then the inductive step. |  |  |
| ③ | Consider the base case in which a  equals  b. |  |  |
| ④ | Consider the base case in which c is zero. |  |  |
| ⑤ | We invoke the derived fact governing addition on the natural numbers: adding zero on the right does not change the number (instantiated for a). | ⑤ | $a + 0 = a$ |
| ⑥ | We invoke the derived fact governing addition on the natural numbers: adding zero on the right does not change the number (instantiated for b). | ⑥ | $b + 0 = b$ |
| ⑦ | From step 4, step 5, and step 6, we can deduce that a plus c equals b plus c. This establishes the base case (see step 4, step 5, and step 6). Hence proven. | ⑦ | $a + c = b + c$ |
| ⑧ | For the inductive step, suppose the claim holds for all smaller values. |  |  |
| ⑨ | Under the supposition in step 8, let k denote the predecessor of c. |  |  |
| ⑩ | Under the supposition in step 8, we cross the inductive boundary: assume the claim holds for a (the induction hypothesis). | ⑩ | $a + k = b + k$ |
| ⑪ | We invoke the definitional clause governing addition on the natural numbers: adding one more on the right bumps the sum by one (instantiated for a, k). | ⑪ | $a + \mathrm{succ}(k) = \mathrm{succ}(a + k)$ |
| ⑫ | We invoke the definitional clause governing addition on the natural numbers: adding one more on the right bumps the sum by one (instantiated for b, k). | ⑫ | $b + \mathrm{succ}(k) = \mathrm{succ}(b + k)$ |
| ⑬ | From step 8, step 9, step 10, step 11, and step 12, this implies a plus c equals b plus c. Hence proven. | ⑬ | $a + c = b + c$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ⑤ | step 4 |
| ⑥ | step 4 |
| ⑦ | step 4, step 5, and step 6 |
| ⑨ | step 8 |
| ⑩ | step 8 |
| ⑬ | step 8, step 9, step 10, step 11, and step 12 |

`equality · equality · equal terms add the same on the right`
