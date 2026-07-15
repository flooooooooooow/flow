# examples.verify.math.derived

*Intersection union difference empty has bounded cardinality.*

**Source.** graham-knuth-patashnik — *Concrete Mathematics*

## Derived fact 1 — card((s ∩ t) ∪ (s \ t)) <= card(s ∪ t)

**Coordinate.** Finset · cardinality · inter union diff empty card bound · **Derived fact**

*Source: graham-knuth-patashnik*

*Built on: inter union diff empty card derived, for cardinality on Finset, union diff inter empty card bound, for cardinality on Finset*

> **Goal.** card((s ∩ t) ∪ (s \ t)) <= card(s ∪ t)
>
> $$\forall s \in Finset \forall t \in Finset\quad card((s ∩ t) ∪ (s \ t)) \le card(s ∪ t)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that inter union diff empty card bound for cardinality on Finset. |  |  |
| ② | We invoke the derived fact governing cardinality on Finset: inter union diff empty card derived, for cardinality on Finset (instantiated for s, t). |  |  |
| ③ | We invoke the derived fact governing cardinality on Finset: union diff inter empty card bound, for cardinality on Finset (instantiated for s, t). |  |  |
| ④ | From step 2 and step 3, this implies card((s ∩ t) ∪ (s \ t)) is at most card(s ∪ t). Hence proven. | ④ | $card((s ∩ t) ∪ (s \ t)) \le card(s ∪ t)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`Finset · cardinality · inter union diff empty card bound`
