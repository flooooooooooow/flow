# examples.verify.math.derived

*Choosing twenty from a successor set.*

**Source.** graham-knuth-patashnik — *Concrete Mathematics*

## Derived fact 1 — choose(succ(n), 20) = choose(n, 19) + choose(n, 20)

**Coordinate.** Comb · choose · choosing twenty from a successor derived · **Derived fact**

*Source: graham-knuth-patashnik*

*Built on: pascal recurrence holds, for choose on Comb, choosing nineteen from a successor derived, for choose on Comb*

> **Goal.** choose(succ(n), 20) = choose(n, 19) + choose(n, 20)
>
> $$\forall n \in \mathbb{N}\quad choose(\mathrm{succ}(n), 20) = choose(n, 19) + choose(n, 20)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that choosing twenty from a successor derived for choose on Comb. |  |  |
| ② | We invoke the definitional clause governing choose on Comb: pascal recurrence holds, for choose on Comb (instantiated for succ(n), 20). |  |  |
| ③ | We invoke the derived fact governing choose on Comb: choosing nineteen from a successor derived, for choose on Comb (instantiated for n). |  |  |
| ④ | From step 2 and step 3, this implies choose(the successor of n, 20) equals choose(n, 19) plus choose(n, 20). Hence proven. | ④ | $choose(\mathrm{succ}(n), 20) = choose(n, 19) + choose(n, 20)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`Comb · choose · choosing twenty from a successor derived`
