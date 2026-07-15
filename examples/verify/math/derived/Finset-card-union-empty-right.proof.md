# examples.verify.math.derived

*Union with the empty set on the right preserves cardinality.*

**Source.** graham-knuth-patashnik — *Concrete Mathematics*

## Derived fact 1 — card(s ∪ empty) = card(s)

**Coordinate.** Finset · cardinality · union with empty on the right preserves size · **Derived fact**

*Source: graham-knuth-patashnik*

*Built on: empty on the right gives the set, for union on Finset, less-or-equal is reflexive, for order on the natural numbers*

> **Goal.** card(s ∪ empty) = card(s)
>
> $$\forall s \in Finset\quad card(s ∪ empty) \le card(s)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that union with empty on the right preserves size for cardinality on Finset. |  |  |
| ② | We invoke the derived fact governing union on Finset: empty on the right gives the set, for union on Finset (instantiated for s). |  |  |
| ③ | We invoke the derived fact governing order on the natural numbers: less-or-equal is reflexive, for order on the natural numbers (instantiated for card(s)). |  |  |
| ④ | From step 2 and step 3, this implies card(s ∪ empty) is at most card(s). Hence proven. | ④ | $card(s ∪ empty) \le card(s)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`Finset · cardinality · union with empty on the right preserves size`
