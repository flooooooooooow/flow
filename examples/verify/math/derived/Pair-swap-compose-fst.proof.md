# examples.verify.math.derived

*Swapping twice restores the first projection.*

**Source.** church — https://en.wikipedia.org/wiki/Product_type

## Derived fact 1 — fst(swap(swap(pair(a, b)))) = a

**Coordinate.** Pair · swap · double swap preserves first projection · **Derived fact**

*Source: church*

*Built on: first component is retrieved, for first projection on Pair, double swap returns the pair, for swap on Pair*

> **Goal.** fst(swap(swap(pair(a, b)))) = a
>
> $$\forall a \in \mathbb{N} \forall b \in \mathbb{N}\quad fst(swap(swap(pair(a, b)))) = a$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that double swap preserves first projection for swap on Pair. |  |  |
| ② | We invoke the definitional clause governing first projection on Pair: first component is retrieved, for first projection on Pair (instantiated for a, b). |  |  |
| ③ | We invoke the derived fact governing swap on Pair: double swap returns the pair, for swap on Pair (instantiated for a, b). |  |  |
| ④ | From step 2 and step 3, this implies fst(swap(swap(pair(a, b)))) equals a. Hence proven. | ④ | $fst(swap(swap(pair(a, b)))) = a$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`Pair · swap · double swap preserves first projection`
