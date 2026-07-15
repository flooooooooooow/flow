# examples.verify.math.derived

*Choosing five from a successor set.*

**Source.** graham-knuth-patashnik — *Concrete Mathematics*

## Derived fact 1 — choose(succ(n), 5) = choose(n, 4) + choose(n, 5)

**Coordinate.** Comb · choose · choosing five from a successor · **Derived fact**

*Source: graham-knuth-patashnik*

*Built on: pascal recurrence holds, for choose on Comb, choosing four from a successor, for choose on Comb*

> **Goal.** choose(succ(n), 5) = choose(n, 4) + choose(n, 5)
>
> $$\forall n \in \mathbb{N}\quad choose(\mathrm{succ}(n), 5) = choose(n, 4) + choose(n, 5)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that choosing five from a successor for choose on Comb. |  |  |
| ② | We invoke the definitional clause governing choose on Comb: pascal recurrence holds, for choose on Comb (instantiated for succ(n), 5). |  |  |
| ③ | We invoke the derived fact governing choose on Comb: choosing four from a successor, for choose on Comb (instantiated for n). |  |  |
| ④ | From step 2 and step 3, this implies choose(the successor of n, 5) equals choose(n, 4) plus choose(n, 5). Hence proven. | ④ | $choose(\mathrm{succ}(n), 5) = choose(n, 4) + choose(n, 5)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`Comb · choose · choosing five from a successor`
