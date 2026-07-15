# examples.verify.math.derived

*First projection commutes with pairing of projections.*

**Source.** church — https://en.wikipedia.org/wiki/Product_type

## Derived fact 1 — fst(pair(fst(p), snd(p))) = fst(p)

**Coordinate.** Pair · first projection · first projection factors through pairing · **Derived fact**

*Source: church*

*Built on: first component is retrieved, for first projection on Pair, second component is retrieved, for second projection on Pair*

> **Goal.** fst(pair(fst(p), snd(p))) = fst(p)
>
> $$\forall a \in \mathbb{N} \forall b \in \mathbb{N}\quad fst(pair(fst(pair(a, b)), snd(pair(a, b)))) = fst(pair(a, b))$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that first projection factors through pairing for first projection on Pair. |  |  |
| ② | We invoke the definitional clause governing first projection on Pair: first component is retrieved, for first projection on Pair (instantiated for a, b). |  |  |
| ③ | We invoke the definitional clause governing second projection on Pair: second component is retrieved, for second projection on Pair (instantiated for a, b). |  |  |
| ④ | From step 2 and step 3, this implies fst(pair(fst(pair(a, b)), snd(pair(a, b)))) equals fst(pair(a, b)). Hence proven. | ④ | $fst(pair(fst(pair(a, b)), snd(pair(a, b)))) = fst(pair(a, b))$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`Pair · first projection · first projection factors through pairing`
