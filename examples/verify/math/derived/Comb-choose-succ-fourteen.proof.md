# examples.verify.math.derived

*Choosing fourteen from a successor set.*

**Source.** graham-knuth-patashnik — *Concrete Mathematics*

## Derived fact 1 — choose(succ(n), 14) = choose(n, 13) + choose(n, 14)

**Coordinate.** Comb · choose · choosing fourteen from a successor · **Derived fact**

*Source: graham-knuth-patashnik*

*Built on: pascal recurrence holds, for choose on Comb, choosing thirteen from a successor, for choose on Comb*

> **Goal.** choose(succ(n), 14) = choose(n, 13) + choose(n, 14)
>
> $$\forall n \in \mathbb{N}\quad choose(\mathrm{succ}(n), 14) = choose(n, 13) + choose(n, 14)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that choosing fourteen from a successor for choose on Comb. |  |  |
| ② | We invoke the definitional clause governing choose on Comb: pascal recurrence holds, for choose on Comb (instantiated for succ(n), 14). |  |  |
| ③ | We invoke the derived fact governing choose on Comb: choosing thirteen from a successor, for choose on Comb (instantiated for n). |  |  |
| ④ | From step 2 and step 3, this implies choose(the successor of n, 14) equals choose(n, 13) plus choose(n, 14). Hence proven. | ④ | $choose(\mathrm{succ}(n), 14) = choose(n, 13) + choose(n, 14)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`Comb · choose · choosing fourteen from a successor`
