# examples.verify.math.derived

*Choosing four from a successor set.*

**Source.** graham-knuth-patashnik — *Concrete Mathematics*

## Derived fact 1 — choose(succ(n), 4) = choose(n, 3) + choose(n, 4)

**Coordinate.** Comb · choose · choosing four from a successor · **Derived fact**

*Source: graham-knuth-patashnik*

*Built on: pascal recurrence holds, for choose on Comb, choosing three from a successor, for choose on Comb*

> **Goal.** choose(succ(n), 4) = choose(n, 3) + choose(n, 4)
>
> $$\forall n \in \mathbb{N}\quad choose(\mathrm{succ}(n), 4) = choose(n, 3) + choose(n, 4)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that choosing four from a successor for choose on Comb. |  |  |
| ② | We invoke the definitional clause governing choose on Comb: pascal recurrence holds, for choose on Comb (instantiated for succ(n), 4). |  |  |
| ③ | We invoke the derived fact governing choose on Comb: choosing three from a successor, for choose on Comb (instantiated for n). |  |  |
| ④ | From step 2 and step 3, this implies choose(the successor of n, 4) equals choose(n, 3) plus choose(n, 4). Hence proven. | ④ | $choose(\mathrm{succ}(n), 4) = choose(n, 3) + choose(n, 4)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`Comb · choose · choosing four from a successor`
