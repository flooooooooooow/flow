# examples.verify.math.derived

*Union intersected with empty vanishes.*

**Source.** graham-knuth-patashnik — *Concrete Mathematics*

## Derived fact 1 — (s ∪ t) ∩ empty = empty

**Coordinate.** Finset · intersection · union intersect empty derived · **Derived fact**

*Source: graham-knuth-patashnik*

*Built on: intersecting with empty gives empty, for intersection on Finset*

> **Goal.** (s ∪ t) ∩ empty = empty
>
> $$\forall s \in Finset \forall t \in Finset\quad (s ∪ t) ∩ empty = empty$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that union intersect empty derived for intersection on Finset. |  |  |
| ② | We invoke the derived fact governing intersection on Finset: intersecting with empty gives empty, for intersection on Finset (instantiated for s ∪ t). |  |  |
| ③ | From step 2, this implies (s ∪ t) ∩ empty equals empty. Hence proven. | ③ | $(s ∪ t) ∩ empty = empty$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ③ | step 2 |

`Finset · intersection · union intersect empty derived`
