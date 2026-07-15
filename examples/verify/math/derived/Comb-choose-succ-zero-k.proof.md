# examples.verify.math.derived

*Choosing zero from a successor set gives one.*

**Source.** graham-knuth-patashnik — *Concrete Mathematics*

## Derived fact 1 — choose(succ(n), 0) = 1

**Coordinate.** Comb · choose · choosing zero from a successor gives one · **Derived fact**

*Source: graham-knuth-patashnik*

*Built on: pascal recurrence holds, for choose on Comb, choosing none gives one, for choose on Comb*

> **Goal.** choose(succ(n), 0) = 1
>
> $$\forall n \in \mathbb{N}\quad choose(\mathrm{succ}(n), 0) = 1$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that choosing zero from a successor gives one for choose on Comb. |  |  |
| ② | We invoke the definitional clause governing choose on Comb: pascal recurrence holds, for choose on Comb (instantiated for succ(n), 0). |  |  |
| ③ | We invoke the definitional clause governing choose on Comb: choosing none gives one, for choose on Comb (instantiated for n). |  |  |
| ④ | From step 2 and step 3, this implies choose(the successor of n, 0) equals 1. Hence proven. | ④ | $choose(\mathrm{succ}(n), 0) = 1$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`Comb · choose · choosing zero from a successor gives one`
