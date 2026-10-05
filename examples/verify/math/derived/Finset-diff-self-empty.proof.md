# examples.verify.math.derived

*Difference of a set with itself is empty.*

**Source.** graham-knuth-patashnik — *Concrete Mathematics*

## Derived fact 1 — s \ s = empty

**Coordinate.** Finset · difference · difference with self is empty · **Derived fact**

*Source: graham-knuth-patashnik*

*Built on: difference with self is empty, for difference on Finset*

> **Goal.** s \ s = empty
>
> $$\forall s \in Finset\quad s \ s = empty$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that difference with self is empty for difference on Finset. |  |  |
| ② | We cross the inductive boundary: assume the claim holds for s (the induction hypothesis). | ② | $s \ s = empty$ |
| ③ | From step 2, this implies s \ s equals empty. Hence proven. | ③ | $s \ s = empty$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ③ | step 2 |

`Finset · difference · difference with self is empty`
