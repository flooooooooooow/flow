# examples.verify.math.derived

*Self-intersection cardinality is bounded by the set size.*

**Source.** graham-knuth-patashnik — *Concrete Mathematics*

## Derived fact 1 — card(s ∩ s) <= card(s)

**Coordinate.** Finset · cardinality · self intersection size is bounded derived · **Derived fact**

*Source: graham-knuth-patashnik*

*Built on: repeating does not change the set, for intersection on Finset, self intersection size is bounded, for cardinality on Finset*

> **Goal.** card(s ∩ s) <= card(s)
>
> $$\forall s \in Finset\quad card(s ∩ s) \le card(s)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that self intersection size is bounded derived for cardinality on Finset. |  |  |
| ② | We invoke the derived fact governing intersection on Finset: repeating does not change the set, for intersection on Finset (instantiated for s). |  |  |
| ③ | We invoke the derived fact governing cardinality on Finset: self intersection size is bounded, for cardinality on Finset (instantiated for s). |  |  |
| ④ | From step 2 and step 3, this implies card(s ∩ s) is at most card(s). Hence proven. | ④ | $card(s ∩ s) \le card(s)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`Finset · cardinality · self intersection size is bounded derived`
