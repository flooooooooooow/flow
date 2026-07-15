# examples.verify.math.derived

*Intersection difference with empty is the intersection.*

**Source.** graham-knuth-patashnik — *Concrete Mathematics*

## Derived fact 1 — (s ∩ t) \ empty = s ∩ t

**Coordinate.** Finset · difference · intersection diff empty derived · **Derived fact**

*Source: graham-knuth-patashnik*

*Built on: difference with empty preserves the set, for difference on Finset*

> **Goal.** (s ∩ t) \ empty = s ∩ t
>
> $$\forall s \in Finset \forall t \in Finset\quad (s ∩ t) \ empty = s ∩ t$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that intersection diff empty derived for difference on Finset. |  |  |
| ② | We invoke the derived fact governing difference on Finset: difference with empty preserves the set, for difference on Finset (instantiated for s ∩ t). |  |  |
| ③ | From step 2, this implies (s ∩ t) \ empty equals s ∩ t. Hence proven. | ③ | $(s ∩ t) \ empty = s ∩ t$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ③ | step 2 |

`Finset · difference · intersection diff empty derived`
