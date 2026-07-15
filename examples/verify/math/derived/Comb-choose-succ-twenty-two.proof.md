# examples.verify.math.derived

*Choosing twenty-two from a successor set.*

**Source.** graham-knuth-patashnik — *Concrete Mathematics*

## Derived fact 1 — choose(succ(n), 22) = choose(n, 21) + choose(n, 22)

**Coordinate.** Comb · choose · choosing twenty two from a successor · **Derived fact**

*Source: graham-knuth-patashnik*

*Built on: pascal recurrence holds, for choose on Comb, choosing twenty one from a successor, for choose on Comb*

> **Goal.** choose(succ(n), 22) = choose(n, 21) + choose(n, 22)
>
> $$\forall n \in \mathbb{N}\quad choose(\mathrm{succ}(n), 22) = choose(n, 21) + choose(n, 22)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that choosing twenty two from a successor for choose on Comb. |  |  |
| ② | We invoke the definitional clause governing choose on Comb: pascal recurrence holds, for choose on Comb (instantiated for succ(n), 22). |  |  |
| ③ | We invoke the derived fact governing choose on Comb: choosing twenty one from a successor, for choose on Comb (instantiated for n). |  |  |
| ④ | From step 2 and step 3, this implies choose(the successor of n, 22) equals choose(n, 21) plus choose(n, 22). Hence proven. | ④ | $choose(\mathrm{succ}(n), 22) = choose(n, 21) + choose(n, 22)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`Comb · choose · choosing twenty two from a successor`
