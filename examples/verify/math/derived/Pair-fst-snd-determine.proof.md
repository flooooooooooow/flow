# examples.verify.math.derived

*First and second projections determine the pair.*

**Source.** church — https://en.wikipedia.org/wiki/Product_type

## Derived fact 1 — fst(pair(a, b)) = a and snd(pair(a, b)) = b

**Coordinate.** Pair · pairing · projections determine components · **Derived fact**

*Source: church*

*Built on: first projection from pairing, for first projection on Pair, second projection from pairing, for second projection on Pair*

> **Goal.** fst(pair(a, b)) = a and snd(pair(a, b)) = b
>
> $$\forall a \in \mathbb{N} \forall b \in \mathbb{N}\quad fst(pair(a, b)) = a$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that projections determine components for pairing on Pair. |  |  |
| ② | We invoke the derived fact governing first projection on Pair: first projection from pairing, for first projection on Pair (instantiated for a, b). |  |  |
| ③ | We invoke the derived fact governing second projection on Pair: second projection from pairing, for second projection on Pair (instantiated for a, b). |  |  |
| ④ | From step 2 and step 3, this implies fst(pair(a, b)) equals a. Hence proven. | ④ | $fst(pair(a, b)) = a$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`Pair · pairing · projections determine components`
