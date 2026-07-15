# examples.verify.math.derived

*Choosing one item from n gives n possibilities.*

**Source.** graham-knuth-patashnik — *Concrete Mathematics*

## Derived fact 1 — choose(n, 1) = n

**Coordinate.** Comb · choose · choosing one gives the count · **Derived fact**

*Source: graham-knuth-patashnik*

*Built on: pascal recurrence holds, for choose on Comb, choosing none gives one, for choose on Comb*

> **Goal.** choose(n, 1) = n
>
> $$\forall n \in \mathbb{N}\quad choose(n, 1) = n$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that choosing one gives the count for choose on Comb. |  |  |
| ② | We invoke the definitional clause governing choose on Comb: choosing none gives one, for choose on Comb (instantiated for pred(n)). |  |  |
| ③ | We invoke the definitional clause governing choose on Comb: pascal recurrence holds, for choose on Comb (instantiated for n, 1). |  |  |
| ④ | From step 2 and step 3, this implies choose(n, 1) equals n. Hence proven. | ④ | $choose(n, 1) = n$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`Comb · choose · choosing one gives the count`
