# examples.verify.math.derived

*Intersection with the empty set on the right yields empty.*

**Source.** graham-knuth-patashnik — *Concrete Mathematics*

## Derived fact 1 — s ∩ empty = empty

**Coordinate.** Finset · intersection · empty on the right gives empty · **Derived fact**

*Source: graham-knuth-patashnik*

*Built on: order does not matter, for intersection on Finset, empty is the right annihilator, for intersection on Finset*

> **Goal.** s ∩ empty = empty
>
> $$\forall s \in Finset\quad s ∩ empty = empty$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that empty on the right gives empty for intersection on Finset. |  |  |
| ② | We invoke the derived fact governing intersection on Finset: order does not matter, for intersection on Finset (instantiated for s, empty). |  |  |
| ③ | We invoke the definitional clause governing intersection on Finset: empty is the right annihilator, for intersection on Finset (instantiated for s). |  |  |
| ④ | From step 2 and step 3, this implies s ∩ empty equals empty. Hence proven. | ④ | $s ∩ empty = empty$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`Finset · intersection · empty on the right gives empty`
