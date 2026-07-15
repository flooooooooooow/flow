# examples.verify.math.derived

*Choosing one element from a successor set.*

**Source.** graham-knuth-patashnik — *Concrete Mathematics*

## Derived fact 1 — choose(succ(n), 1) = succ(n)

**Coordinate.** Comb · choose · choosing one from a successor · **Derived fact**

*Source: graham-knuth-patashnik*

*Built on: pascal recurrence holds, for choose on Comb, choosing none gives one, for choose on Comb*

> **Goal.** choose(succ(n), 1) = succ(n)
>
> $$\forall n \in \mathbb{N}\quad choose(\mathrm{succ}(n), 1) = \mathrm{succ}(n)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that choosing one from a successor for choose on Comb. |  |  |
| ② | We invoke the definitional clause governing choose on Comb: pascal recurrence holds, for choose on Comb (instantiated for succ(n), 1). |  |  |
| ③ | We invoke the definitional clause governing choose on Comb: choosing none gives one, for choose on Comb (instantiated for n). |  |  |
| ④ | From step 2 and step 3, this implies choose(the successor of n, 1) equals the successor of n. Hence proven. | ④ | $choose(\mathrm{succ}(n), 1) = \mathrm{succ}(n)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`Comb · choose · choosing one from a successor`
