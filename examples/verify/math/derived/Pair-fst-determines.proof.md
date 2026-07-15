# examples.verify.math.derived

*First projection determines the first component.*

**Source.** church — https://en.wikipedia.org/wiki/Product_type

## Derived fact 1 — fst(pair(a, b)) = a

**Coordinate.** Pair · first projection · first component determines · **Derived fact**

*Source: church*

*Built on: first projection from pairing, for first projection on Pair*

> **Goal.** fst(pair(a, b)) = a
>
> $$\forall a \in \mathbb{N} \forall b \in \mathbb{N}\quad fst(pair(a, b)) = a$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that first component determines for first projection on Pair. |  |  |
| ② | We invoke the derived fact governing first projection on Pair: first projection from pairing, for first projection on Pair (instantiated for a, b). |  |  |
| ③ | From step 2, this implies fst(pair(a, b)) equals a. Hence proven. | ③ | $fst(pair(a, b)) = a$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ③ | step 2 |

`Pair · first projection · first component determines`
