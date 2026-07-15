# examples.verify.math.derived

*Intersection with the empty set on the left yields empty.*

**Source.** graham-knuth-patashnik — *Concrete Mathematics*

## Derived fact 1 — empty ∩ s = empty

**Coordinate.** Finset · intersection · empty on the left gives empty · **Derived fact**

*Source: graham-knuth-patashnik*

*Built on: order does not matter, for intersection on Finset, empty is the left annihilator, for intersection on Finset*

> **Goal.** empty ∩ s = empty
>
> $$\forall s \in Finset\quad empty ∩ s = empty$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that empty on the left gives empty for intersection on Finset. |  |  |
| ② | We invoke the derived fact governing intersection on Finset: order does not matter, for intersection on Finset (instantiated for empty, s). |  |  |
| ③ | We invoke the definitional clause governing intersection on Finset: empty is the left annihilator, for intersection on Finset (instantiated for s). |  |  |
| ④ | From step 2 and step 3, this implies empty ∩ s equals empty. Hence proven. | ④ | $empty ∩ s = empty$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`Finset · intersection · empty on the left gives empty`
