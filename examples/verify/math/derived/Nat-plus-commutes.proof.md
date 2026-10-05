# examples.verify.math.derived

*Addition commutes: a + b = b + a.*

**Source.** landau — *Foundations of Analysis*, Ch. 1

## Derived fact 1 — You can swap the order of addition

**Coordinate.** the natural numbers · addition · order does not matter · **Derived fact**

*Source: landau — https://en.wikipedia.org/wiki/Foundations_of_analysis_(book)*

*Built on: adding zero on the left does not change the number, adding zero on the right does not change the number, adding one more on the right bumps the sum by one*

> **Goal.** You can swap the order of addition.  (3 + 5 = 5 + 3)
>
> $$\forall a \in \mathbb{N} \forall b \in \mathbb{N}\quad a + b = b + a$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that order does not matter for addition on the natural numbers. |  |  |
| ② | We proceed by induction on a: first the base case, then the inductive step. |  |  |
| ③ | Consider the base case in which a is zero. |  |  |
| ④ | We invoke the derived fact governing addition on the natural numbers: adding zero on the right does not change the number (instantiated for b). | ④ | $b + 0 = b$ |
| ⑤ | We invoke the definitional clause governing addition on the natural numbers: adding zero on the left does not change the number (instantiated for b). | ⑤ | $0 + b = b$ |
| ⑥ | From step 3, step 4, and step 5, we can deduce that a plus b equals b plus a. This establishes the base case (see step 3, step 4, and step 5). Hence proven. | ⑥ | $a + b = b + a$ |
| ⑦ | For the inductive step, suppose the claim holds for all smaller values. |  |  |
| ⑧ | Under the supposition in step 7, let n denote the predecessor of a. |  |  |
| ⑨ | Under the supposition in step 7, we cross the inductive boundary: assume the claim holds for n (the induction hypothesis). | ⑨ | $n + b = b + n$ |
| ⑩ | We invoke the definitional clause governing addition on the natural numbers: adding one more on the right bumps the sum by one (instantiated for n, b). | ⑩ | $n + \mathrm{succ}(b) = \mathrm{succ}(n + b)$ |
| ⑪ | From step 7, step 8, step 9, and step 10, this implies a plus b equals b plus a. Hence proven. | ⑪ | $a + b = b + a$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 3 |
| ⑤ | step 3 |
| ⑥ | step 3, step 4, and step 5 |
| ⑧ | step 7 |
| ⑨ | step 7 |
| ⑪ | step 7, step 8, step 9, and step 10 |

`the natural numbers · addition · order does not matter`
