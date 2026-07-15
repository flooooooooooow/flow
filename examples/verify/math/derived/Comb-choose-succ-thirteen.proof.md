# examples.verify.math.derived

*Choosing thirteen from a successor set.*

**Source.** graham-knuth-patashnik — *Concrete Mathematics*

## Derived fact 1 — choose(succ(n), 13) = choose(n, 12) + choose(n, 13)

**Coordinate.** Comb · choose · choosing thirteen from a successor · **Derived fact**

*Source: graham-knuth-patashnik*

*Built on: pascal recurrence holds, for choose on Comb, choosing twelve from a successor, for choose on Comb*

> **Goal.** choose(succ(n), 13) = choose(n, 12) + choose(n, 13)
>
> $$\forall n \in \mathbb{N}\quad choose(\mathrm{succ}(n), 13) = choose(n, 12) + choose(n, 13)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that choosing thirteen from a successor for choose on Comb. |  |  |
| ② | We invoke the definitional clause governing choose on Comb: pascal recurrence holds, for choose on Comb (instantiated for succ(n), 13). |  |  |
| ③ | We invoke the derived fact governing choose on Comb: choosing twelve from a successor, for choose on Comb (instantiated for n). |  |  |
| ④ | From step 2 and step 3, this implies choose(the successor of n, 13) equals choose(n, 12) plus choose(n, 13). Hence proven. | ④ | $choose(\mathrm{succ}(n), 13) = choose(n, 12) + choose(n, 13)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`Comb · choose · choosing thirteen from a successor`
