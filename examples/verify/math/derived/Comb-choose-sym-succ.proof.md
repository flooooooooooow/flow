# examples.verify.math.derived

*Symmetry of binomial coefficients at a successor index.*

**Source.** graham-knuth-patashnik — *Concrete Mathematics*

## Derived fact 1 — choose(succ(n), k) = choose(succ(n), succ(n) - k)

**Coordinate.** Comb · choose · symmetry at successors · **Derived fact**

*Source: graham-knuth-patashnik*

*Built on: symmetry in k and n minus k, for choose on Comb, choosing none gives one, for choose on Comb*

> **Goal.** choose(succ(n), k) = choose(succ(n), succ(n) - k)
>
> $$\forall n \in \mathbb{N} \forall k \in \mathbb{N}\quad choose(\mathrm{succ}(n), k) = choose(\mathrm{succ}(n), \mathrm{succ}(n) - k)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that symmetry at successors for choose on Comb. |  |  |
| ② | We invoke the derived fact governing choose on Comb: symmetry in k and n minus k, for choose on Comb (instantiated for succ(n), k). |  |  |
| ③ | We invoke the definitional clause governing choose on Comb: choosing none gives one, for choose on Comb (instantiated for n). |  |  |
| ④ | From step 2 and step 3, this implies choose(the successor of n, k) equals choose(the successor of n, the successor of n - k). Hence proven. | ④ | $choose(\mathrm{succ}(n), k) = choose(\mathrm{succ}(n), \mathrm{succ}(n) - k)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`Comb · choose · symmetry at successors`
