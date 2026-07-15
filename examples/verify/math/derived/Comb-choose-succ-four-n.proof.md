# examples.verify.math.derived

*Choosing four from a successor derived from Pascal.*

**Source.** graham-knuth-patashnik — *Concrete Mathematics*

## Derived fact 1 — choose(succ(n), 4) = choose(n, 3) + choose(n, 4)

**Coordinate.** Comb · choose · choosing four from a successor derived · **Derived fact**

*Source: graham-knuth-patashnik*

*Built on: choosing four from a successor, for choose on Comb*

> **Goal.** choose(succ(n), 4) = choose(n, 3) + choose(n, 4)
>
> $$\forall n \in \mathbb{N}\quad choose(\mathrm{succ}(n), 4) = choose(n, 3) + choose(n, 4)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that choosing four from a successor derived for choose on Comb. |  |  |
| ② | We invoke the derived fact governing choose on Comb: choosing four from a successor, for choose on Comb (instantiated for n). |  |  |
| ③ | From step 2, this implies choose(the successor of n, 4) equals choose(n, 3) plus choose(n, 4). Hence proven. | ③ | $choose(\mathrm{succ}(n), 4) = choose(n, 3) + choose(n, 4)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ③ | step 2 |

`Comb · choose · choosing four from a successor derived`
