# examples.verify.math.derived

*Pascal recurrence at the top edge gives one.*

**Source.** graham-knuth-patashnik — *Concrete Mathematics*

## Derived fact 1 — choose(n, n) = 1 via Pascal at the diagonal

**Coordinate.** Comb · choose · Pascal recurrence closes on the diagonal · **Derived fact**

*Source: graham-knuth-patashnik*

*Built on: choosing all gives one, for choose on Comb, pascal recurrence holds, for choose on Comb*

> **Goal.** choose(n, n) = 1 via Pascal at the diagonal
>
> $$\forall n \in \mathbb{N}\quad choose(n, n) = 1$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that pascal recurrence closes on the diagonal for choose on Comb. |  |  |
| ② | We invoke the derived fact governing choose on Comb: choosing all gives one, for choose on Comb (instantiated for n). |  |  |
| ③ | We invoke the definitional clause governing choose on Comb: pascal recurrence holds, for choose on Comb (instantiated for n, n). |  |  |
| ④ | From step 2 and step 3, this implies choose(n, n) equals 1. Hence proven. | ④ | $choose(n, n) = 1$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`Comb · choose · Pascal recurrence closes on the diagonal`
