# examples.verify.math.derived

*Choosing eighteen from a successor set.*

**Source.** graham-knuth-patashnik — *Concrete Mathematics*

## Derived fact 1 — choose(succ(n), 18) = choose(n, 17) + choose(n, 18)

**Coordinate.** Comb · choose · choosing eighteen from a successor derived · **Derived fact**

*Source: graham-knuth-patashnik*

*Built on: pascal recurrence holds, for choose on Comb, choosing seventeen from a successor derived, for choose on Comb*

> **Goal.** choose(succ(n), 18) = choose(n, 17) + choose(n, 18)
>
> $$\forall n \in \mathbb{N}\quad choose(\mathrm{succ}(n), 18) = choose(n, 17) + choose(n, 18)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that choosing eighteen from a successor derived for choose on Comb. |  |  |
| ② | We invoke the definitional clause governing choose on Comb: pascal recurrence holds, for choose on Comb (instantiated for succ(n), 18). |  |  |
| ③ | We invoke the derived fact governing choose on Comb: choosing seventeen from a successor derived, for choose on Comb (instantiated for n). |  |  |
| ④ | From step 2 and step 3, this implies choose(the successor of n, 18) equals choose(n, 17) plus choose(n, 18). Hence proven. | ④ | $choose(\mathrm{succ}(n), 18) = choose(n, 17) + choose(n, 18)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`Comb · choose · choosing eighteen from a successor derived`
