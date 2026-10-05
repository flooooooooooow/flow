# examples.verify.math.derived

*Choosing six from a successor set.*

**Source.** graham-knuth-patashnik — *Concrete Mathematics*

## Derived fact 1 — choose(succ(n), 6) = choose(n, 5) + choose(n, 6)

**Coordinate.** Comb · choose · choosing six from a successor · **Derived fact**

*Source: graham-knuth-patashnik*

*Built on: pascal recurrence holds, for choose on Comb, choosing five from a successor, for choose on Comb*

> **Goal.** choose(succ(n), 6) = choose(n, 5) + choose(n, 6)
>
> $$\forall n \in \mathbb{N}\quad choose(\mathrm{succ}(n), 6) = choose(n, 5) + choose(n, 6)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that choosing six from a successor for choose on Comb. |  |  |
| ② | We invoke the definitional clause governing choose on Comb: pascal recurrence holds, for choose on Comb (instantiated for succ(n), 6). |  |  |
| ③ | We invoke the derived fact governing choose on Comb: choosing five from a successor, for choose on Comb (instantiated for n). |  |  |
| ④ | From step 2 and step 3, this implies choose(the successor of n, 6) equals choose(n, 5) plus choose(n, 6). Hence proven. | ④ | $choose(\mathrm{succ}(n), 6) = choose(n, 5) + choose(n, 6)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`Comb · choose · choosing six from a successor`
