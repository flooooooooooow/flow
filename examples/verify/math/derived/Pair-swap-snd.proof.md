# examples.verify.math.derived

*Swapping exchanges the second projection.*

**Source.** church — https://en.wikipedia.org/wiki/Product_type

## Derived fact 1 — snd(swap(pair(a, b))) = a

**Coordinate.** Pair · swap · swap exchanges the second projection · **Derived fact**

*Source: church*

*Built on: first component is retrieved, for first projection on Pair, second component is retrieved, for second projection on Pair, double swap returns the pair, for swap on Pair*

> **Goal.** snd(swap(pair(a, b))) = a
>
> $$\forall a \in \mathbb{N} \forall b \in \mathbb{N}\quad snd(swap(pair(a, b))) = a$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that swap exchanges the second projection for swap on Pair. |  |  |
| ② | We invoke the definitional clause governing first projection on Pair: first component is retrieved, for first projection on Pair (instantiated for a, b). |  |  |
| ③ | We invoke the definitional clause governing second projection on Pair: second component is retrieved, for second projection on Pair (instantiated for a, b). |  |  |
| ④ | We invoke the derived fact governing swap on Pair: double swap returns the pair, for swap on Pair (instantiated for a, b). |  |  |
| ⑤ | From step 2, step 3, and step 4, this implies snd(swap(pair(a, b))) equals a. Hence proven. | ⑤ | $snd(swap(pair(a, b))) = a$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ⑤ | step 2, step 3, and step 4 |

`Pair · swap · swap exchanges the second projection`
