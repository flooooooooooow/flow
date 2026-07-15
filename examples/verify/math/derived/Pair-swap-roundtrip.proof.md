# examples.verify.math.derived

*Swapping pair components twice recovers the original pair.*

**Source.** church — https://en.wikipedia.org/wiki/Product_type

## Derived fact 1 — swap(swap(pair(a, b))) = pair(a, b)

**Coordinate.** Pair · swap · double swap returns the pair · **Derived fact**

*Source: church*

*Built on: first component is retrieved, for first projection on Pair, second component is retrieved, for second projection on Pair, components determine the pair, for pairing on Pair*

> **Goal.** swap(swap(pair(a, b))) = pair(a, b)
>
> $$\forall a \in \mathbb{N} \forall b \in \mathbb{N}\quad swap(swap(pair(a, b))) = pair(a, b)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that double swap returns the pair for swap on Pair. |  |  |
| ② | We invoke the definitional clause governing first projection on Pair: first component is retrieved, for first projection on Pair (instantiated for a, b). |  |  |
| ③ | We invoke the definitional clause governing second projection on Pair: second component is retrieved, for second projection on Pair (instantiated for a, b). |  |  |
| ④ | We invoke the derived fact governing pairing on Pair: components determine the pair, for pairing on Pair (instantiated for a, b). |  |  |
| ⑤ | From step 2, step 3, and step 4, this implies swap(swap(pair(a, b))) equals pair(a, b). Hence proven. | ⑤ | $swap(swap(pair(a, b))) = pair(a, b)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ⑤ | step 2, step 3, and step 4 |

`Pair · swap · double swap returns the pair`
