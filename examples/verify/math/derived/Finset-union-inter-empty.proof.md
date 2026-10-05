# examples.verify.math.derived

*Union then intersecting with empty yields empty.*

**Source.** graham-knuth-patashnik — *Concrete Mathematics*

## Derived fact 1 — (a ∪ b) ∩ empty = empty

**Coordinate.** Finset · intersection · union with empty on the right annihilates · **Derived fact**

*Source: graham-knuth-patashnik*

*Built on: empty on the right gives empty, for intersection on Finset, order does not matter, for union on Finset*

> **Goal.** (a ∪ b) ∩ empty = empty
>
> $$\forall a \in Finset \forall b \in Finset\quad (a ∪ b) ∩ empty = empty$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that union with empty on the right annihilates for intersection on Finset. |  |  |
| ② | We invoke the derived fact governing intersection on Finset: empty on the right gives empty, for intersection on Finset (instantiated for a ∪ b). |  |  |
| ③ | We invoke the derived fact governing union on Finset: order does not matter, for union on Finset (instantiated for a, b). |  |  |
| ④ | From step 2 and step 3, this implies (a ∪ b) ∩ empty equals empty. Hence proven. | ④ | $(a ∪ b) ∩ empty = empty$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`Finset · intersection · union with empty on the right annihilates`
