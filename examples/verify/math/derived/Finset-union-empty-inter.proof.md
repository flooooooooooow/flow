# examples.verify.math.derived

*Union with empty then intersecting yields empty.*

**Source.** graham-knuth-patashnik — *Concrete Mathematics*

## Derived fact 1 — (s ∪ empty) ∩ empty = empty

**Coordinate.** Finset · intersection · union empty then intersect empty · **Derived fact**

*Source: graham-knuth-patashnik*

*Built on: empty on the right gives the set, for union on Finset, empty on the right gives empty, for intersection on Finset*

> **Goal.** (s ∪ empty) ∩ empty = empty
>
> $$\forall s \in Finset\quad (s ∪ empty) ∩ empty = empty$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that union empty then intersect empty for intersection on Finset. |  |  |
| ② | We invoke the derived fact governing union on Finset: empty on the right gives the set, for union on Finset (instantiated for s). |  |  |
| ③ | We invoke the derived fact governing intersection on Finset: empty on the right gives empty, for intersection on Finset (instantiated for s ∪ empty). |  |  |
| ④ | From step 2 and step 3, this implies (s ∪ empty) ∩ empty equals empty. Hence proven. | ④ | $(s ∪ empty) ∩ empty = empty$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`Finset · intersection · union empty then intersect empty`
