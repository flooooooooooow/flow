# examples.verify.math.derived

*Swapping recovers both components of a pair.*

**Source.** church — https://en.wikipedia.org/wiki/Product_type

## Derived fact 1 — fst(swap(pair(a, b))) = b and snd(swap(pair(a, b))) = a

**Coordinate.** Pair · swap · swap recovers both components · **Derived fact**

*Source: church*

*Built on: swap exchanges components, for swap on Pair, first projection from pairing, for first projection on Pair*

> **Goal.** fst(swap(pair(a, b))) = b and snd(swap(pair(a, b))) = a
>
> $$\forall a \in \mathbb{N} \forall b \in \mathbb{N}\quad fst(swap(pair(a, b))) = b$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that swap recovers both components for swap on Pair. |  |  |
| ② | We invoke the derived fact governing swap on Pair: swap exchanges components, for swap on Pair (instantiated for a, b). |  |  |
| ③ | We invoke the derived fact governing first projection on Pair: first projection from pairing, for first projection on Pair (instantiated for b, a). |  |  |
| ④ | From step 2 and step 3, this implies fst(swap(pair(a, b))) equals b. Hence proven. | ④ | $fst(swap(pair(a, b))) = b$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`Pair · swap · swap recovers both components`
