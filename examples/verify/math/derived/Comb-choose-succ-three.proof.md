# examples.verify.math.derived

*Choosing three from a successor set.*

**Source.** graham-knuth-patashnik — *Concrete Mathematics*

## Derived fact 1 — choose(succ(n), 3) = choose(n, 2) + choose(n, 3)

**Coordinate.** Comb · choose · choosing three from a successor · **Derived fact**

*Source: graham-knuth-patashnik*

*Built on: pascal recurrence holds, for choose on Comb, choosing two via Pascal, for choose on Comb*

> **Goal.** choose(succ(n), 3) = choose(n, 2) + choose(n, 3)
>
> $$\forall n \in \mathbb{N}\quad choose(\mathrm{succ}(n), 3) = choose(n, 2) + choose(n, 3)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that choosing three from a successor for choose on Comb. |  |  |
| ② | We invoke the definitional clause governing choose on Comb: pascal recurrence holds, for choose on Comb (instantiated for succ(n), 3). |  |  |
| ③ | We invoke the derived fact governing choose on Comb: choosing two via Pascal, for choose on Comb (instantiated for n). |  |  |
| ④ | From step 2 and step 3, this implies choose(the successor of n, 3) equals choose(n, 2) plus choose(n, 3). Hence proven. | ④ | $choose(\mathrm{succ}(n), 3) = choose(n, 2) + choose(n, 3)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`Comb · choose · choosing three from a successor`
