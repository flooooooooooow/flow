# examples.verify.math.derived

*The empty set unioned on the left has cardinality zero.*

**Source.** graham-knuth-patashnik — *Concrete Mathematics*

## Derived fact 1 — card(empty ∪ s) <= card(s)

**Coordinate.** Finset · cardinality · empty left union has bounded size · **Derived fact**

*Source: graham-knuth-patashnik*

*Built on: empty on the left gives the set, for union on Finset, the empty set has size zero, for cardinality on Finset*

> **Goal.** card(empty ∪ s) <= card(s)
>
> $$\forall s \in Finset\quad card(empty ∪ s) \le card(s)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that empty left union has bounded size for cardinality on Finset. |  |  |
| ② | We invoke the derived fact governing union on Finset: empty on the left gives the set, for union on Finset (instantiated for s). |  |  |
| ③ | We invoke the definitional clause governing cardinality on Finset: the empty set has size zero, for cardinality on Finset. |  |  |
| ④ | From step 2 and step 3, this implies card(empty ∪ s) is at most card(s). Hence proven. | ④ | $card(empty ∪ s) \le card(s)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`Finset · cardinality · empty left union has bounded size`
