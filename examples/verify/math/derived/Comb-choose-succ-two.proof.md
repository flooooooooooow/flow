# examples.verify.math.derived

*Choosing two from a successor set.*

**Source.** graham-knuth-patashnik — *Concrete Mathematics*

## Derived fact 1 — choose(succ(n), 2) = choose(n, 1) + choose(n, 2)

**Coordinate.** Comb · choose · choosing two from a successor · **Derived fact**

*Source: graham-knuth-patashnik*

*Built on: pascal recurrence holds, for choose on Comb, choosing one gives the count, for choose on Comb*

> **Goal.** choose(succ(n), 2) = choose(n, 1) + choose(n, 2)
>
> $$\forall n \in \mathbb{N}\quad choose(\mathrm{succ}(n), 2) = choose(n, 1) + choose(n, 2)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that choosing two from a successor for choose on Comb. |  |  |
| ② | We invoke the definitional clause governing choose on Comb: pascal recurrence holds, for choose on Comb (instantiated for succ(n), 2). |  |  |
| ③ | We invoke the derived fact governing choose on Comb: choosing one gives the count, for choose on Comb (instantiated for n). |  |  |
| ④ | From step 2 and step 3, this implies choose(the successor of n, 2) equals choose(n, 1) plus choose(n, 2). Hence proven. | ④ | $choose(\mathrm{succ}(n), 2) = choose(n, 1) + choose(n, 2)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`Comb · choose · choosing two from a successor`
