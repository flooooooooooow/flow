# examples.verify.math.derived

*Choosing nineteen from a successor set.*

**Source.** graham-knuth-patashnik — *Concrete Mathematics*

## Derived fact 1 — choose(succ(n), 19) = choose(n, 18) + choose(n, 19)

**Coordinate.** Comb · choose · choosing nineteen from a successor · **Derived fact**

*Source: graham-knuth-patashnik*

*Built on: pascal recurrence holds, for choose on Comb, choosing eighteen from a successor, for choose on Comb*

> **Goal.** choose(succ(n), 19) = choose(n, 18) + choose(n, 19)
>
> $$\forall n \in \mathbb{N}\quad choose(\mathrm{succ}(n), 19) = choose(n, 18) + choose(n, 19)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that choosing nineteen from a successor for choose on Comb. |  |  |
| ② | We invoke the definitional clause governing choose on Comb: pascal recurrence holds, for choose on Comb (instantiated for succ(n), 19). |  |  |
| ③ | We invoke the derived fact governing choose on Comb: choosing eighteen from a successor, for choose on Comb (instantiated for n). |  |  |
| ④ | From step 2 and step 3, this implies choose(the successor of n, 19) equals choose(n, 18) plus choose(n, 19). Hence proven. | ④ | $choose(\mathrm{succ}(n), 19) = choose(n, 18) + choose(n, 19)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`Comb · choose · choosing nineteen from a successor`
