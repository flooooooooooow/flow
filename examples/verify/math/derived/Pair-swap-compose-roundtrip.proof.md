# examples.verify.math.derived

*Composing swap twice is the identity on pairs.*

**Source.** church — https://en.wikipedia.org/wiki/Product_type

## Derived fact 1 — swap(swap(pair(a, b))) = pair(a, b)

**Coordinate.** Pair · swap · compose swap twice is identity · **Derived fact**

*Source: church*

*Built on: swap recovers both components, for swap on Pair, swap recovers second as first, for swap on Pair*

> **Goal.** swap(swap(pair(a, b))) = pair(a, b)
>
> $$\forall a \in \mathbb{N} \forall b \in \mathbb{N}\quad swap(swap(pair(a, b))) = pair(a, b)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that compose swap twice is identity for swap on Pair. |  |  |
| ② | We invoke the derived fact governing swap on Pair: swap recovers both components, for swap on Pair (instantiated for a, b). |  |  |
| ③ | We invoke the derived fact governing swap on Pair: swap recovers second as first, for swap on Pair (instantiated for a, b). |  |  |
| ④ | From step 2 and step 3, this implies swap(swap(pair(a, b))) equals pair(a, b). Hence proven. | ④ | $swap(swap(pair(a, b))) = pair(a, b)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`Pair · swap · compose swap twice is identity`
