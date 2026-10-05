# examples.verify.math.derived

*Choosing fifteen from a successor set.*

**Source.** graham-knuth-patashnik — *Concrete Mathematics*

## Derived fact 1 — choose(succ(n), 15) = choose(n, 14) + choose(n, 15)

**Coordinate.** Comb · choose · choosing fifteen from a successor · **Derived fact**

*Source: graham-knuth-patashnik*

*Built on: pascal recurrence holds, for choose on Comb, choosing fourteen from a successor, for choose on Comb*

> **Goal.** choose(succ(n), 15) = choose(n, 14) + choose(n, 15)
>
> $$\forall n \in \mathbb{N}\quad choose(\mathrm{succ}(n), 15) = choose(n, 14) + choose(n, 15)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that choosing fifteen from a successor for choose on Comb. |  |  |
| ② | We invoke the definitional clause governing choose on Comb: pascal recurrence holds, for choose on Comb (instantiated for succ(n), 15). |  |  |
| ③ | We invoke the derived fact governing choose on Comb: choosing fourteen from a successor, for choose on Comb (instantiated for n). |  |  |
| ④ | From step 2 and step 3, this implies choose(the successor of n, 15) equals choose(n, 14) plus choose(n, 15). Hence proven. | ④ | $choose(\mathrm{succ}(n), 15) = choose(n, 14) + choose(n, 15)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`Comb · choose · choosing fifteen from a successor`
