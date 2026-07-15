# examples.verify.math.derived

*Union cardinality bounds intersection cardinality from below.*

**Source.** graham-knuth-patashnik — *Concrete Mathematics*

## Derived fact 1 — card(s ∩ t) <= card(s ∪ t)

**Coordinate.** Finset · cardinality · union bounds intersection card derived · **Derived fact**

*Source: graham-knuth-patashnik*

*Built on: intersection card at most union card, for cardinality on Finset*

> **Goal.** card(s ∩ t) <= card(s ∪ t)
>
> $$\forall s \in Finset \forall t \in Finset\quad card(s ∩ t) \le card(s ∪ t)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that union bounds intersection card derived for cardinality on Finset. |  |  |
| ② | We invoke the derived fact governing cardinality on Finset: intersection card at most union card, for cardinality on Finset (instantiated for s, t). |  |  |
| ③ | From step 2, this implies card(s ∩ t) is at most card(s ∪ t). Hence proven. | ③ | $card(s ∩ t) \le card(s ∪ t)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ③ | step 2 |

`Finset · cardinality · union bounds intersection card derived`
