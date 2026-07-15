# examples.verify.math.derived

*Intersection with itself leaves a finite set unchanged.*

**Source.** graham-knuth-patashnik — *Concrete Mathematics*

## Derived fact 1 — s ∩ s = s

**Coordinate.** Finset · intersection · repeating does not change the set · **Derived fact**

*Source: graham-knuth-patashnik*

*Built on: order does not matter, for intersection on Finset, empty is the right annihilator, for intersection on Finset*

> **Goal.** s ∩ s = s
>
> $$\forall s \in Finset\quad s ∩ s = s$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that repeating does not change the set for intersection on Finset. |  |  |
| ② | We invoke the derived fact governing intersection on Finset: order does not matter, for intersection on Finset (instantiated for s, s). |  |  |
| ③ | We invoke the definitional clause governing intersection on Finset: empty is the right annihilator, for intersection on Finset (instantiated for empty). |  |  |
| ④ | From step 2 and step 3, this implies s ∩ s equals s. Hence proven. | ④ | $s ∩ s = s$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`Finset · intersection · repeating does not change the set`
