# examples.verify.math.derived

*Union difference with self is empty.*

**Source.** graham-knuth-patashnik — *Concrete Mathematics*

## Derived fact 1 — (s ∪ t) \ (s ∪ t) = empty

**Coordinate.** Finset · difference · union diff self is empty · **Derived fact**

*Source: graham-knuth-patashnik*

*Built on: difference with self is empty, for difference on Finset*

> **Goal.** (s ∪ t) \ (s ∪ t) = empty
>
> $$\forall s \in Finset \forall t \in Finset\quad (s ∪ t) \ (s ∪ t) = empty$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that union diff self is empty for difference on Finset. |  |  |
| ② | We invoke the derived fact governing difference on Finset: difference with self is empty, for difference on Finset (instantiated for s ∪ t). |  |  |
| ③ | From step 2, this implies (s ∪ t) \ (s ∪ t) equals empty. Hence proven. | ③ | $(s ∪ t) \ (s ∪ t) = empty$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ③ | step 2 |

`Finset · difference · union diff self is empty`
