# examples.verify.math.derived

*Choosing all items from a successor set gives one.*

**Source.** graham-knuth-patashnik — *Concrete Mathematics*

## Derived fact 1 — choose(succ(n), succ(n)) = 1

**Coordinate.** Comb · choose · choosing all from a successor · **Derived fact**

*Source: graham-knuth-patashnik*

*Built on: choosing all gives one, for choose on Comb, choosing none gives one, for choose on Comb*

> **Goal.** choose(succ(n), succ(n)) = 1
>
> $$\forall n \in \mathbb{N}\quad choose(\mathrm{succ}(n), \mathrm{succ}(n)) = 1$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that choosing all from a successor for choose on Comb. |  |  |
| ② | We invoke the derived fact governing choose on Comb: choosing all gives one, for choose on Comb (instantiated for succ(n)). |  |  |
| ③ | We invoke the definitional clause governing choose on Comb: choosing none gives one, for choose on Comb (instantiated for n). |  |  |
| ④ | From step 2 and step 3, this implies choose(the successor of n, the successor of n) equals 1. Hence proven. | ④ | $choose(\mathrm{succ}(n), \mathrm{succ}(n)) = 1$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`Comb · choose · choosing all from a successor`
