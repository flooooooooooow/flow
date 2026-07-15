# examples.verify.math.derived

*Self-difference has cardinality zero.*

**Source.** graham-knuth-patashnik — *Concrete Mathematics*

## Derived fact 1 — card(s \ s) = 0

**Coordinate.** Finset · cardinality · self difference has card zero · **Derived fact**

*Source: graham-knuth-patashnik*

*Built on: difference with self is empty, for difference on Finset, empty set has cardinality zero, for cardinality on Finset*

> **Goal.** card(s \ s) = 0
>
> $$\forall s \in Finset\quad card(s \ s) = 0$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that self difference has card zero for cardinality on Finset. |  |  |
| ② | We invoke the derived fact governing difference on Finset: difference with self is empty, for difference on Finset (instantiated for s). |  |  |
| ③ | We invoke the derived fact governing cardinality on Finset: empty set has cardinality zero, for cardinality on Finset. |  |  |
| ④ | From step 2 and step 3, this implies card(s \ s) equals 0. Hence proven. | ④ | $card(s \ s) = 0$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`Finset · cardinality · self difference has card zero`
