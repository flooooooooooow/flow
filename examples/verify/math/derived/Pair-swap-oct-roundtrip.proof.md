# examples.verify.math.derived

*Octuple swap returns the original pair.*

**Source.** church — https://en.wikipedia.org/wiki/Product_type

## Derived fact 1 — eight nested swaps on a pair returns the pair

**Coordinate.** Pair · swap · octuple swap returns pair · **Derived fact**

*Source: church*

*Built on: septuple swap returns pair, for swap on Pair, sextuple swap returns pair, for swap on Pair*

> **Goal.** eight nested swaps on a pair returns the pair
>
> $$\forall a \in \mathbb{N} \forall b \in \mathbb{N}\quad swap(swap(swap(swap(swap(swap(swap(swap(pair(a, b))))))))) = pair(a, b)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that octuple swap returns pair for swap on Pair. |  |  |
| ② | We invoke the derived fact governing swap on Pair: septuple swap returns pair, for swap on Pair (instantiated for a, b). |  |  |
| ③ | We invoke the derived fact governing swap on Pair: sextuple swap returns pair, for swap on Pair (instantiated for a, b). |  |  |
| ④ | From step 2 and step 3, this implies swap(swap(swap(swap(swap(swap(swap(swap(pair(a, b))))))))) equals pair(a, b). Hence proven. | ④ | $swap(swap(swap(swap(swap(swap(swap(swap(pair(a, b))))))))) = pair(a, b)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`Pair · swap · octuple swap returns pair`
