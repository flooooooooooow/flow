# examples.verify.math.derived

*Choosing all items from n gives exactly one subset.*

**Source.** graham-knuth-patashnik — *Concrete Mathematics*

## Derived fact 1 — choose(n, n) = 1

**Coordinate.** Comb · choose · choosing all gives one · **Derived fact**

*Source: graham-knuth-patashnik*

*Built on: choosing none gives one, for choose on Comb, symmetry in k and n minus k, for choose on Comb*

> **Goal.** choose(n, n) = 1
>
> $$\forall n \in \mathbb{N}\quad choose(n, n) = 1$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that choosing all gives one for choose on Comb. |  |  |
| ② | We invoke the definitional clause governing choose on Comb: choosing none gives one, for choose on Comb (instantiated for n). |  |  |
| ③ | We invoke the derived fact governing choose on Comb: symmetry in k and n minus k, for choose on Comb (instantiated for n, n). |  |  |
| ④ | From step 2 and step 3, this implies choose(n, n) equals 1. Hence proven. | ④ | $choose(n, n) = 1$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`Comb · choose · choosing all gives one`
