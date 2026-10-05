# examples.verify.math.derived

*Union with itself leaves a finite set unchanged.*

**Source.** graham-knuth-patashnik — *Concrete Mathematics*

## Derived fact 1 — s ∪ s = s

**Coordinate.** Finset · union · repeating does not change the set · **Derived fact**

*Source: graham-knuth-patashnik*

*Built on: order does not matter, for union on Finset, empty is the right identity, for union on Finset*

> **Goal.** s ∪ s = s
>
> $$\forall s \in Finset\quad s ∪ s = s$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that repeating does not change the set for union on Finset. |  |  |
| ② | We invoke the derived fact governing union on Finset: order does not matter, for union on Finset (instantiated for s, s). |  |  |
| ③ | We invoke the definitional clause governing union on Finset: empty is the right identity, for union on Finset (instantiated for s). |  |  |
| ④ | From step 2 and step 3, this implies s ∪ s equals s. Hence proven. | ④ | $s ∪ s = s$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`Finset · union · repeating does not change the set`
