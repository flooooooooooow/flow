# examples.verify.math.derived

*Intersection difference with empty preserves cardinality.*

**Source.** graham-knuth-patashnik — *Concrete Mathematics*

## Derived fact 1 — card((s ∩ t) \ empty) = card(s ∩ t)

**Coordinate.** Finset · cardinality · inter diff empty card derived · **Derived fact**

*Source: graham-knuth-patashnik*

*Built on: inter diff empty is intersection, for difference on Finset, inter union empty card derived, for cardinality on Finset*

> **Goal.** card((s ∩ t) \ empty) = card(s ∩ t)
>
> $$\forall s \in Finset \forall t \in Finset\quad card((s ∩ t) \ empty) = card(s ∩ t)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that inter diff empty card derived for cardinality on Finset. |  |  |
| ② | We invoke the derived fact governing difference on Finset: inter diff empty is intersection, for difference on Finset (instantiated for s, t). |  |  |
| ③ | We invoke the derived fact governing cardinality on Finset: inter union empty card derived, for cardinality on Finset (instantiated for s, t). |  |  |
| ④ | From step 2 and step 3, this implies card((s ∩ t) \ empty) equals card(s ∩ t). Hence proven. | ④ | $card((s ∩ t) \ empty) = card(s ∩ t)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`Finset · cardinality · inter diff empty card derived`
