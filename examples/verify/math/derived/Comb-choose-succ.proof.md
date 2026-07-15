# examples.verify.math.derived

*Pascal recurrence at a successor index.*

**Source.** graham-knuth-patashnik — *Concrete Mathematics*

## Derived fact 1 — choose(succ(n), succ(k)) = choose(n, k) + choose(n, succ(k))

**Coordinate.** Comb · choose · Pascal recurrence at successors · **Derived fact**

*Source: graham-knuth-patashnik*

*Built on: pascal recurrence holds, for choose on Comb, choosing none gives one, for choose on Comb*

> **Goal.** choose(succ(n), succ(k)) = choose(n, k) + choose(n, succ(k))
>
> $$\forall n \in \mathbb{N} \forall k \in \mathbb{N}\quad choose(\mathrm{succ}(n), \mathrm{succ}(k)) = choose(n, k) + choose(n, \mathrm{succ}(k))$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that pascal recurrence at successors for choose on Comb. |  |  |
| ② | We invoke the definitional clause governing choose on Comb: pascal recurrence holds, for choose on Comb (instantiated for succ(n), succ(k)). |  |  |
| ③ | We invoke the definitional clause governing choose on Comb: choosing none gives one, for choose on Comb (instantiated for n). |  |  |
| ④ | From step 2 and step 3, this implies choose(the successor of n, the successor of k) equals choose(n, k) plus choose(n, the successor of k). Hence proven. | ④ | $choose(\mathrm{succ}(n), \mathrm{succ}(k)) = choose(n, k) + choose(n, \mathrm{succ}(k))$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`Comb · choose · Pascal recurrence at successors`
