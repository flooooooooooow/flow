# examples.verify.math.derived

*Choosing seventeen from a successor set.*

**Source.** graham-knuth-patashnik — *Concrete Mathematics*

## Derived fact 1 — choose(succ(n), 17) = choose(n, 16) + choose(n, 17)

**Coordinate.** Comb · choose · choosing seventeen from a successor · **Derived fact**

*Source: graham-knuth-patashnik*

*Built on: pascal recurrence holds, for choose on Comb, choosing sixteen from a successor, for choose on Comb*

> **Goal.** choose(succ(n), 17) = choose(n, 16) + choose(n, 17)
>
> $$\forall n \in \mathbb{N}\quad choose(\mathrm{succ}(n), 17) = choose(n, 16) + choose(n, 17)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that choosing seventeen from a successor for choose on Comb. |  |  |
| ② | We invoke the definitional clause governing choose on Comb: pascal recurrence holds, for choose on Comb (instantiated for succ(n), 17). |  |  |
| ③ | We invoke the derived fact governing choose on Comb: choosing sixteen from a successor, for choose on Comb (instantiated for n). |  |  |
| ④ | From step 2 and step 3, this implies choose(the successor of n, 17) equals choose(n, 16) plus choose(n, 17). Hence proven. | ④ | $choose(\mathrm{succ}(n), 17) = choose(n, 16) + choose(n, 17)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`Comb · choose · choosing seventeen from a successor`
