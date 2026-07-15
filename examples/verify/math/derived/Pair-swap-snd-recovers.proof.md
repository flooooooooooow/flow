# examples.verify.math.derived

*Swapping recovers the second component as first.*

**Source.** church — https://en.wikipedia.org/wiki/Product_type

## Derived fact 1 — snd(swap(pair(a, b))) = a

**Coordinate.** Pair · swap · swap recovers second as first · **Derived fact**

*Source: church*

*Built on: swap exchanges components, for swap on Pair, second projection from pairing, for second projection on Pair*

> **Goal.** snd(swap(pair(a, b))) = a
>
> $$\forall a \in \mathbb{N} \forall b \in \mathbb{N}\quad snd(swap(pair(a, b))) = a$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that swap recovers second as first for swap on Pair. |  |  |
| ② | We invoke the derived fact governing swap on Pair: swap exchanges components, for swap on Pair (instantiated for a, b). |  |  |
| ③ | We invoke the derived fact governing second projection on Pair: second projection from pairing, for second projection on Pair (instantiated for b, a). |  |  |
| ④ | From step 2 and step 3, this implies snd(swap(pair(a, b))) equals a. Hence proven. | ④ | $snd(swap(pair(a, b))) = a$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`Pair · swap · swap recovers second as first`
