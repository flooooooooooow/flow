# examples.verify.math.derived

*Choosing twenty-nine from a successor set.*

**Source.** graham-knuth-patashnik — *Concrete Mathematics*

## Derived fact 1 — choose(succ(n), 29) = choose(n, 28) + choose(n, 29)

**Coordinate.** Comb · choose · choosing twenty nine from a successor · **Derived fact**

*Source: graham-knuth-patashnik*

*Built on: pascal recurrence holds, for choose on Comb, choosing twenty eight from a successor, for choose on Comb*

> **Goal.** choose(succ(n), 29) = choose(n, 28) + choose(n, 29)
>
> $$\forall n \in \mathbb{N}\quad choose(\mathrm{succ}(n), 29) = choose(n, 28) + choose(n, 29)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that choosing twenty nine from a successor for choose on Comb. |  |  |
| ② | We invoke the definitional clause governing choose on Comb: pascal recurrence holds, for choose on Comb (instantiated for succ(n), 29). |  |  |
| ③ | We invoke the derived fact governing choose on Comb: choosing twenty eight from a successor, for choose on Comb (instantiated for n). |  |  |
| ④ | From step 2 and step 3, this implies choose(the successor of n, 29) equals choose(n, 28) plus choose(n, 29). Hence proven. | ④ | $choose(\mathrm{succ}(n), 29) = choose(n, 28) + choose(n, 29)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`Comb · choose · choosing twenty nine from a successor`
