# examples.verify.math.derived

*Swapping twice restores the second projection.*

**Source.** church — https://en.wikipedia.org/wiki/Product_type

## Derived fact 1 — snd(swap(swap(pair(a, b)))) = b

**Coordinate.** Pair · swap · double swap preserves second projection · **Derived fact**

*Source: church*

*Built on: second component is retrieved, for second projection on Pair, double swap returns the pair, for swap on Pair*

> **Goal.** snd(swap(swap(pair(a, b)))) = b
>
> $$\forall a \in \mathbb{N} \forall b \in \mathbb{N}\quad snd(swap(swap(pair(a, b)))) = b$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that double swap preserves second projection for swap on Pair. |  |  |
| ② | We invoke the definitional clause governing second projection on Pair: second component is retrieved, for second projection on Pair (instantiated for a, b). |  |  |
| ③ | We invoke the derived fact governing swap on Pair: double swap returns the pair, for swap on Pair (instantiated for a, b). |  |  |
| ④ | From step 2 and step 3, this implies snd(swap(swap(pair(a, b)))) equals b. Hence proven. | ④ | $snd(swap(swap(pair(a, b)))) = b$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`Pair · swap · double swap preserves second projection`
