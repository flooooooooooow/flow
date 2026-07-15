# examples.verify.math.derived

*Choosing twenty-six from a successor set.*

**Source.** graham-knuth-patashnik — *Concrete Mathematics*

## Derived fact 1 — choose(succ(n), 26) = choose(n, 25) + choose(n, 26)

**Coordinate.** Comb · choose · choosing twenty six from a successor · **Derived fact**

*Source: graham-knuth-patashnik*

*Built on: pascal recurrence holds, for choose on Comb, choosing twenty five from a successor, for choose on Comb*

> **Goal.** choose(succ(n), 26) = choose(n, 25) + choose(n, 26)
>
> $$\forall n \in \mathbb{N}\quad choose(\mathrm{succ}(n), 26) = choose(n, 25) + choose(n, 26)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that choosing twenty six from a successor for choose on Comb. |  |  |
| ② | We invoke the definitional clause governing choose on Comb: pascal recurrence holds, for choose on Comb (instantiated for succ(n), 26). |  |  |
| ③ | We invoke the derived fact governing choose on Comb: choosing twenty five from a successor, for choose on Comb (instantiated for n). |  |  |
| ④ | From step 2 and step 3, this implies choose(the successor of n, 26) equals choose(n, 25) plus choose(n, 26). Hence proven. | ④ | $choose(\mathrm{succ}(n), 26) = choose(n, 25) + choose(n, 26)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`Comb · choose · choosing twenty six from a successor`
