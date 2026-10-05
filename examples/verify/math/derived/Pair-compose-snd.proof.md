# examples.verify.math.derived

*Second projection commutes with pairing of projections.*

**Source.** church — https://en.wikipedia.org/wiki/Product_type

## Derived fact 1 — snd(pair(fst(p), snd(p))) = snd(p)

**Coordinate.** Pair · second projection · second projection factors through pairing · **Derived fact**

*Source: church*

*Built on: first component is retrieved, for first projection on Pair, second component is retrieved, for second projection on Pair*

> **Goal.** snd(pair(fst(p), snd(p))) = snd(p)
>
> $$\forall a \in \mathbb{N} \forall b \in \mathbb{N}\quad snd(pair(fst(pair(a, b)), snd(pair(a, b)))) = snd(pair(a, b))$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that second projection factors through pairing for second projection on Pair. |  |  |
| ② | We invoke the definitional clause governing first projection on Pair: first component is retrieved, for first projection on Pair (instantiated for a, b). |  |  |
| ③ | We invoke the definitional clause governing second projection on Pair: second component is retrieved, for second projection on Pair (instantiated for a, b). |  |  |
| ④ | From step 2 and step 3, this implies snd(pair(fst(pair(a, b)), snd(pair(a, b)))) equals snd(pair(a, b)). Hence proven. | ④ | $snd(pair(fst(pair(a, b)), snd(pair(a, b)))) = snd(pair(a, b))$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`Pair · second projection · second projection factors through pairing`
