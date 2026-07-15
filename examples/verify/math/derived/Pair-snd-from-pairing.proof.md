# examples.verify.math.derived

*Second projection retrieves the second component.*

**Source.** church — https://en.wikipedia.org/wiki/Product_type

## Derived fact 1 — snd(pair(a, b)) = b

**Coordinate.** Pair · second projection · second projection from pairing · **Derived fact**

*Source: church*

*Built on: second component is retrieved, for second projection on Pair*

> **Goal.** snd(pair(a, b)) = b
>
> $$\forall a \in \mathbb{N} \forall b \in \mathbb{N}\quad snd(pair(a, b)) = b$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that second projection from pairing for second projection on Pair. |  |  |
| ② | We invoke the definitional clause governing second projection on Pair: second component is retrieved, for second projection on Pair (instantiated for a, b). |  |  |
| ③ | From step 2, this implies snd(pair(a, b)) equals b. Hence proven. | ③ | $snd(pair(a, b)) = b$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ③ | step 2 |

`Pair · second projection · second projection from pairing`
