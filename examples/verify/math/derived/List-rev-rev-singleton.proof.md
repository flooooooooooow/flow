# examples.verify.math.derived

*Double reverse fixes a singleton list.*

**Source.** church — https://en.wikipedia.org/wiki/List_(abstract_data_type)

## Derived fact 1 — rev(rev(cons(x, nil))) = cons(x, nil)

**Coordinate.** List · reverse · double reverse fixes singletons · **Derived fact**

*Source: church*

*Built on: double reverse returns the list, for reverse on List*

> **Goal.** rev(rev(cons(x, nil))) = cons(x, nil)
>
> $$\forall x \in \mathbb{N}\quad rev(rev(cons(x, nil))) = cons(x, nil)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that double reverse fixes singletons for reverse on List. |  |  |
| ② | We invoke the derived fact governing reverse on List: double reverse returns the list, for reverse on List (instantiated for cons(x, nil)). |  |  |
| ③ | From step 2, this implies rev(rev(cons(x, nil))) equals cons(x, nil). Hence proven. | ③ | $rev(rev(cons(x, nil))) = cons(x, nil)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ③ | step 2 |

`List · reverse · double reverse fixes singletons`
