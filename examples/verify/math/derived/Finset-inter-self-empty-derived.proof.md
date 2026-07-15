# examples.verify.math.derived

*Self-intersection is empty when intersected with empty.*

**Source.** graham-knuth-patashnik — *Concrete Mathematics*

## Derived fact 1 — (s ∩ s) ∩ empty = empty

**Coordinate.** Finset · intersection · self intersect empty derived · **Derived fact**

*Source: graham-knuth-patashnik*

*Built on: self intersect empty is empty, for intersection on Finset*

> **Goal.** (s ∩ s) ∩ empty = empty
>
> $$\forall s \in Finset\quad (s ∩ s) ∩ empty = empty$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that self intersect empty derived for intersection on Finset. |  |  |
| ② | We invoke the derived fact governing intersection on Finset: self intersect empty is empty, for intersection on Finset (instantiated for s). |  |  |
| ③ | From step 2, this implies (s ∩ s) ∩ empty equals empty. Hence proven. | ③ | $(s ∩ s) ∩ empty = empty$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ③ | step 2 |

`Finset · intersection · self intersect empty derived`
