# examples.verify.math.derived

*Binomial coefficients are symmetric in k and n-k.*

**Source.** graham-knuth-patashnik — *Concrete Mathematics*

## Derived fact 1 — choose(n, k) = choose(n, n - k)

**Coordinate.** Comb · choose · symmetry in k and n minus k · **Derived fact**

*Source: graham-knuth-patashnik*

*Built on: pascal recurrence holds, for choose on Comb, choosing none gives one, for choose on Comb*

> **Goal.** choose(n, k) = choose(n, n - k)
>
> $$\forall n \in \mathbb{N} \forall k \in \mathbb{N}\quad choose(n, k) = choose(n, n - k)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that symmetry in k and n minus k for choose on Comb. |  |  |
| ② | We proceed by induction on n: first the base case, then the inductive step. |  |  |
| ③ | Consider the base case in which k is zero. |  |  |
| ④ | We invoke the definitional clause governing choose on Comb: choosing none gives one, for choose on Comb (instantiated for n). |  |  |
| ⑤ | From step 3 and step 4, we can deduce that choose(n, k) equals choose(n, n - k). This establishes the base case (see step 3 and step 4). Hence proven. | ⑤ | $choose(n, k) = choose(n, n - k)$ |
| ⑥ | For the inductive step, suppose the claim holds for all smaller values. |  |  |
| ⑦ | Under the supposition in step 6, let j denote the predecessor of k. |  |  |
| ⑧ | Under the supposition in step 6, we cross the inductive boundary: assume the claim holds for pred(n) (the induction hypothesis). | ⑧ | $choose(pred(n), j) = choose(pred(n), pred(n) - j)$ |
| ⑨ | We invoke the definitional clause governing choose on Comb: pascal recurrence holds, for choose on Comb (instantiated for n, k). |  |  |
| ⑩ | From step 6, step 7, step 8, and step 9, this implies choose(n, k) equals choose(n, n - k). Hence proven. | ⑩ | $choose(n, k) = choose(n, n - k)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 3 |
| ⑤ | step 3 and step 4 |
| ⑦ | step 6 |
| ⑧ | step 6 |
| ⑩ | step 6, step 7, step 8, and step 9 |

`Comb · choose · symmetry in k and n minus k`
