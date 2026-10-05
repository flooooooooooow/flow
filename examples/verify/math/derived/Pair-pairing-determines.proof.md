# examples.verify.math.derived

*Pairing is determined by its components.*

**Source.** church — https://en.wikipedia.org/wiki/Product_type

## Derived fact 1 — pair(a, b) determines a and b

**Coordinate.** Pair · pairing · pairing is determined by components · **Derived fact**

*Source: church*

*Built on: first projection from pairing, for first projection on Pair, second projection from pairing, for second projection on Pair, components determine the pair, for pairing on Pair*

> **Goal.** pair(a, b) determines a and b
>
> $$\forall a \in \mathbb{N} \forall b \in \mathbb{N}\quad pair(a, b) = pair(a, b)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that pairing is determined by components for pairing on Pair. |  |  |
| ② | We invoke the derived fact governing first projection on Pair: first projection from pairing, for first projection on Pair (instantiated for a, b). |  |  |
| ③ | We invoke the derived fact governing second projection on Pair: second projection from pairing, for second projection on Pair (instantiated for a, b). |  |  |
| ④ | We invoke the derived fact governing pairing on Pair: components determine the pair, for pairing on Pair (instantiated for a, b). |  |  |
| ⑤ | From step 2, step 3, and step 4, this implies pair(a, b) equals pair(a, b). Hence proven. | ⑤ | $pair(a, b) = pair(a, b)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ⑤ | step 2, step 3, and step 4 |

`Pair · pairing · pairing is determined by components`
