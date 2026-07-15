# examples.verify.math.derived

*Pairing projections recovers the original pair.*

**Source.** church — https://en.wikipedia.org/wiki/Product_type

## Derived fact 1 — pair(a, b) = pair(fst(pair(a, b)), snd(pair(a, b)))

**Coordinate.** Pair · pairing · pairing recovers projections · **Derived fact**

*Source: church*

*Built on: first component is retrieved, for first projection on Pair, second component is retrieved, for second projection on Pair, components determine the pair, for pairing on Pair*

> **Goal.** pair(a, b) = pair(fst(pair(a, b)), snd(pair(a, b)))
>
> $$\forall a \in \mathbb{N} \forall b \in \mathbb{N}\quad pair(a, b) = pair(fst(pair(a, b)), snd(pair(a, b)))$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that pairing recovers projections for pairing on Pair. |  |  |
| ② | We invoke the definitional clause governing first projection on Pair: first component is retrieved, for first projection on Pair (instantiated for a, b). |  |  |
| ③ | We invoke the definitional clause governing second projection on Pair: second component is retrieved, for second projection on Pair (instantiated for a, b). |  |  |
| ④ | We invoke the derived fact governing pairing on Pair: components determine the pair, for pairing on Pair (instantiated for a, b). |  |  |
| ⑤ | From step 2, step 3, and step 4, this implies pair(a, b) equals pair(fst(pair(a, b)), snd(pair(a, b))). Hence proven. | ⑤ | $pair(a, b) = pair(fst(pair(a, b)), snd(pair(a, b)))$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ⑤ | step 2, step 3, and step 4 |

`Pair · pairing · pairing recovers projections`
