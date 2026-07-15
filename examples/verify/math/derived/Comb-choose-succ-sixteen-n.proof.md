# examples.verify.math.derived

*Choosing sixteen from a successor set.*

**Source.** graham-knuth-patashnik — *Concrete Mathematics*

## Derived fact 1 — choose(succ(n), 16) = choose(n, 15) + choose(n, 16)

**Coordinate.** Comb · choose · choosing sixteen from a successor derived · **Derived fact**

*Source: graham-knuth-patashnik*

*Built on: pascal recurrence holds, for choose on Comb, choosing fifteen from a successor, for choose on Comb*

> **Goal.** choose(succ(n), 16) = choose(n, 15) + choose(n, 16)
>
> $$\forall n \in \mathbb{N}\quad choose(\mathrm{succ}(n), 16) = choose(n, 15) + choose(n, 16)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that choosing sixteen from a successor derived for choose on Comb. |  |  |
| ② | We invoke the definitional clause governing choose on Comb: pascal recurrence holds, for choose on Comb (instantiated for succ(n), 16). |  |  |
| ③ | We invoke the derived fact governing choose on Comb: choosing fifteen from a successor, for choose on Comb (instantiated for n). |  |  |
| ④ | From step 2 and step 3, this implies choose(the successor of n, 16) equals choose(n, 15) plus choose(n, 16). Hence proven. | ④ | $choose(\mathrm{succ}(n), 16) = choose(n, 15) + choose(n, 16)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`Comb · choose · choosing sixteen from a successor derived`
