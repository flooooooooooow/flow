# examples.verify.math.derived

*Choosing two items relates to choosing one by Pascal.*

**Source.** graham-knuth-patashnik — *Concrete Mathematics*

## Derived fact 1 — choose(n, 2) = choose(n, 1) + choose(n - 1, 1) for n > 1

**Coordinate.** Comb · choose · choosing two via Pascal · **Derived fact**

*Source: graham-knuth-patashnik*

*Built on: choosing one gives the count, for choose on Comb, pascal recurrence holds, for choose on Comb*

> **Goal.** choose(n, 2) = choose(n, 1) + choose(n - 1, 1) for n > 1
>
> $$\forall n \in \mathbb{N}\quad choose(n, 2) = choose(n, 1) + choose(pred(n), 1)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that choosing two via Pascal for choose on Comb. |  |  |
| ② | We split into exhaustive cases — the claim must hold in each one. |  |  |
| ③ | Case 1 (see step 2): suppose n is zero. |  |  |
| ④ | We invoke the derived fact governing choose on Comb: choosing one gives the count, for choose on Comb (instantiated for 0). |  |  |
| ⑤ | From step 3 and step 4, this implies choose(n, 2) equals choose(n, 1) plus choose(pred(n), 1) in this case. | ⑤ | $choose(n, 2) = choose(n, 1) + choose(pred(n), 1)$ |
| ⑥ | Case 2 (see step 2): neither disjunct holds. |  |  |
| ⑦ | Let k = 2. |  |  |
| ⑧ | We invoke the definitional clause governing choose on Comb: pascal recurrence holds, for choose on Comb (instantiated for n, k). |  |  |
| ⑨ | We invoke the derived fact governing choose on Comb: choosing one gives the count, for choose on Comb (instantiated for n). |  |  |
| ⑩ | From step 6, step 7, step 8, and step 9, this implies choose(n, 2) equals choose(n, 1) plus choose(pred(n), 1). Together with the other cases (step 3 and step 6), the goal is discharged. Hence proven. | ⑩ | $choose(n, 2) = choose(n, 1) + choose(pred(n), 1)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ③ | step 2 |
| ⑤ | step 3 and step 4 |
| ⑥ | step 2 |
| ⑩ | step 6, step 7, step 8, and step 9 |

`Comb · choose · choosing two via Pascal`
