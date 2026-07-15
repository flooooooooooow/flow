# examples.verify.math.derived

*Union with the empty set on the left changes nothing.*

**Source.** graham-knuth-patashnik — *Concrete Mathematics*

## Derived fact 1 — empty ∪ s = s

**Coordinate.** Finset · union · empty on the left gives the set · **Derived fact**

*Source: graham-knuth-patashnik*

*Built on: order does not matter, for union on Finset, empty is the left identity, for union on Finset*

> **Goal.** empty ∪ s = s
>
> $$\forall s \in Finset\quad empty ∪ s = s$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that empty on the left gives the set for union on Finset. |  |  |
| ② | We invoke the derived fact governing union on Finset: order does not matter, for union on Finset (instantiated for empty, s). |  |  |
| ③ | We invoke the definitional clause governing union on Finset: empty is the left identity, for union on Finset (instantiated for s). |  |  |
| ④ | From step 2 and step 3, this implies empty ∪ s equals s. Hence proven. | ④ | $empty ∪ s = s$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`Finset · union · empty on the left gives the set`
