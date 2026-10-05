# examples.verify.math.derived

*Self-union intersected with empty is empty.*

**Source.** graham-knuth-patashnik — *Concrete Mathematics*

## Derived fact 1 — (s ∪ s) ∩ empty = empty

**Coordinate.** Finset · intersection · self union intersect empty is empty · **Derived fact**

*Source: graham-knuth-patashnik*

*Built on: repeating does not change the set, for union on Finset, empty on the right gives empty, for intersection on Finset*

> **Goal.** (s ∪ s) ∩ empty = empty
>
> $$\forall s \in Finset\quad (s ∪ s) ∩ empty = empty$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that self union intersect empty is empty for intersection on Finset. |  |  |
| ② | We invoke the derived fact governing union on Finset: repeating does not change the set, for union on Finset (instantiated for s). |  |  |
| ③ | We invoke the derived fact governing intersection on Finset: empty on the right gives empty, for intersection on Finset (instantiated for s ∪ s). |  |  |
| ④ | From step 2 and step 3, this implies (s ∪ s) ∩ empty equals empty. Hence proven. | ④ | $(s ∪ s) ∩ empty = empty$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`Finset · intersection · self union intersect empty is empty`
