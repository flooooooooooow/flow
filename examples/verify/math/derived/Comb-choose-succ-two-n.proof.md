# examples.verify.math.derived

*Choosing two from a successor gives a successor count.*

**Source.** graham-knuth-patashnik — *Concrete Mathematics*

## Derived fact 1 — choose(succ(n), 2) = choose(n, 1) + choose(n, 2)

**Coordinate.** Comb · choose · choosing two from a successor derived · **Derived fact**

*Source: graham-knuth-patashnik*

*Built on: choosing two from a successor, for choose on Comb*

> **Goal.** choose(succ(n), 2) = choose(n, 1) + choose(n, 2)
>
> $$\forall n \in \mathbb{N}\quad choose(\mathrm{succ}(n), 2) = choose(n, 1) + choose(n, 2)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that choosing two from a successor derived for choose on Comb. |  |  |
| ② | We invoke the derived fact governing choose on Comb: choosing two from a successor, for choose on Comb (instantiated for n). |  |  |
| ③ | From step 2, this implies choose(the successor of n, 2) equals choose(n, 1) plus choose(n, 2). Hence proven. | ③ | $choose(\mathrm{succ}(n), 2) = choose(n, 1) + choose(n, 2)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ③ | step 2 |

`Comb · choose · choosing two from a successor derived`
