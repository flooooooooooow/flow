# examples.verify.math.derived

*Choosing from zero items gives zero when k is positive.*

**Source.** graham-knuth-patashnik — *Concrete Mathematics*

## Derived fact 1 — choose(0, k) = 0 for k > 0

**Coordinate.** Comb · choose · choosing from empty gives zero when k is positive · **Derived fact**

*Source: graham-knuth-patashnik*

*Built on: choosing none gives one, for choose on Comb, pascal recurrence holds, for choose on Comb*

> **Goal.** choose(0, k) = 0 for k > 0
>
> $$\forall k \in \mathbb{N}\quad choose(0, k) = 0$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that choosing from empty gives zero when k is positive for choose on Comb. |  |  |
| ② | We split into exhaustive cases — the claim must hold in each one. |  |  |
| ③ | Case 1 (see step 2): suppose k is zero. |  |  |
| ④ | We invoke the definitional clause governing choose on Comb: choosing none gives one, for choose on Comb (instantiated for 0). |  |  |
| ⑤ | From step 3 and step 4, this implies choose(0, k) equals 0 in this case. | ⑤ | $choose(0, k) = 0$ |
| ⑥ | Case 2 (see step 2): neither disjunct holds. |  |  |
| ⑦ | Let j denote the predecessor of k. |  |  |
| ⑧ | We invoke the definitional clause governing choose on Comb: pascal recurrence holds, for choose on Comb (instantiated for 0, k). |  |  |
| ⑨ | From step 6, step 7, and step 8, this implies choose(0, k) equals 0. Together with the other cases (step 3 and step 6), the goal is discharged. Hence proven. | ⑨ | $choose(0, k) = 0$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ③ | step 2 |
| ⑤ | step 3 and step 4 |
| ⑥ | step 2 |
| ⑨ | step 6, step 7, and step 8 |

`Comb · choose · choosing from empty gives zero when k is positive`
