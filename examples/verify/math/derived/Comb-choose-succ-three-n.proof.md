# examples.verify.math.derived

*Choosing three from a successor derived from Pascal.*

**Source.** graham-knuth-patashnik — *Concrete Mathematics*

## Derived fact 1 — choose(succ(n), 3) = choose(n, 2) + choose(n, 3)

**Coordinate.** Comb · choose · choosing three from a successor derived · **Derived fact**

*Source: graham-knuth-patashnik*

*Built on: choosing three from a successor, for choose on Comb*

> **Goal.** choose(succ(n), 3) = choose(n, 2) + choose(n, 3)
>
> $$\forall n \in \mathbb{N}\quad choose(\mathrm{succ}(n), 3) = choose(n, 2) + choose(n, 3)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that choosing three from a successor derived for choose on Comb. |  |  |
| ② | We invoke the derived fact governing choose on Comb: choosing three from a successor, for choose on Comb (instantiated for n). |  |  |
| ③ | From step 2, this implies choose(the successor of n, 3) equals choose(n, 2) plus choose(n, 3). Hence proven. | ③ | $choose(\mathrm{succ}(n), 3) = choose(n, 2) + choose(n, 3)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ③ | step 2 |

`Comb · choose · choosing three from a successor derived`
