# examples.verify.math.derived

*Undecuple swap returns the original pair.*

**Source.** church — https://en.wikipedia.org/wiki/Product_type

## Derived fact 1 — eleven nested swaps on a pair returns the pair

**Coordinate.** Pair · swap · undecuple swap returns pair · **Derived fact**

*Source: church*

*Built on: decuple swap returns pair, for swap on Pair, nonuple swap returns pair, for swap on Pair*

> **Goal.** eleven nested swaps on a pair returns the pair
>
> $$\forall a \in \mathbb{N} \forall b \in \mathbb{N}\quad swap(swap(swap(swap(swap(swap(swap(swap(swap(swap(swap(pair(a, b))))))))))) = pair(a, b)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that undecuple swap returns pair for swap on Pair. |  |  |
| ② | We invoke the derived fact governing swap on Pair: decuple swap returns pair, for swap on Pair (instantiated for a, b). |  |  |
| ③ | We invoke the derived fact governing swap on Pair: nonuple swap returns pair, for swap on Pair (instantiated for a, b). |  |  |
| ④ | From step 2 and step 3, this implies swap(swap(swap(swap(swap(swap(swap(swap(swap(swap(swap(pair(a, b))))))))))) equals pair(a, b). Hence proven. | ④ | $swap(swap(swap(swap(swap(swap(swap(swap(swap(swap(swap(pair(a, b))))))))))) = pair(a, b)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`Pair · swap · undecuple swap returns pair`
