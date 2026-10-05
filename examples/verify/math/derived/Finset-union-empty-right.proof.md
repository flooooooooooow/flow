# examples.verify.math.derived

*Union with the empty set on the right changes nothing.*

**Source.** graham-knuth-patashnik — *Concrete Mathematics*

## Derived fact 1 — s ∪ empty = s

**Coordinate.** Finset · union · empty on the right gives the set · **Derived fact**

*Source: graham-knuth-patashnik*

*Built on: order does not matter, for union on Finset, empty is the right identity, for union on Finset*

> **Goal.** s ∪ empty = s
>
> $$\forall s \in Finset\quad s ∪ empty = s$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that empty on the right gives the set for union on Finset. |  |  |
| ② | We invoke the derived fact governing union on Finset: order does not matter, for union on Finset (instantiated for s, empty). |  |  |
| ③ | We invoke the definitional clause governing union on Finset: empty is the right identity, for union on Finset (instantiated for s). |  |  |
| ④ | From step 2 and step 3, this implies s ∪ empty equals s. Hence proven. | ④ | $s ∪ empty = s$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`Finset · union · empty on the right gives the set`
