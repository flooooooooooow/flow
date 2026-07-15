# examples.verify.math.derived

*Difference of intersection with empty is the intersection.*

**Source.** graham-knuth-patashnik — *Concrete Mathematics*

## Derived fact 1 — (s ∩ t) \ empty = s ∩ t

**Coordinate.** Finset · difference · inter diff empty is intersection · **Derived fact**

*Source: graham-knuth-patashnik*

*Built on: intersection diff empty derived, for difference on Finset*

> **Goal.** (s ∩ t) \ empty = s ∩ t
>
> $$\forall s \in Finset \forall t \in Finset\quad (s ∩ t) \ empty = s ∩ t$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that inter diff empty is intersection for difference on Finset. |  |  |
| ② | We invoke the derived fact governing difference on Finset: intersection diff empty derived, for difference on Finset (instantiated for s, t). |  |  |
| ③ | From step 2, this implies (s ∩ t) \ empty equals s ∩ t. Hence proven. | ③ | $(s ∩ t) \ empty = s ∩ t$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ③ | step 2 |

`Finset · difference · inter diff empty is intersection`
