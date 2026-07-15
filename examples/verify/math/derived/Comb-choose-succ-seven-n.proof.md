# examples.verify.math.derived

*Choosing seven from a successor set.*

**Source.** graham-knuth-patashnik — *Concrete Mathematics*

## Derived fact 1 — choose(succ(n), 7) = choose(n, 6) + choose(n, 7)

**Coordinate.** Comb · choose · choosing seven from a successor derived · **Derived fact**

*Source: graham-knuth-patashnik*

*Built on: pascal recurrence holds, for choose on Comb, choosing six from a successor, for choose on Comb*

> **Goal.** choose(succ(n), 7) = choose(n, 6) + choose(n, 7)
>
> $$\forall n \in \mathbb{N}\quad choose(\mathrm{succ}(n), 7) = choose(n, 6) + choose(n, 7)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that choosing seven from a successor derived for choose on Comb. |  |  |
| ② | We invoke the definitional clause governing choose on Comb: pascal recurrence holds, for choose on Comb (instantiated for succ(n), 7). |  |  |
| ③ | We invoke the derived fact governing choose on Comb: choosing six from a successor, for choose on Comb (instantiated for n). |  |  |
| ④ | From step 2 and step 3, this implies choose(the successor of n, 7) equals choose(n, 6) plus choose(n, 7). Hence proven. | ④ | $choose(\mathrm{succ}(n), 7) = choose(n, 6) + choose(n, 7)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`Comb · choose · choosing seven from a successor derived`
