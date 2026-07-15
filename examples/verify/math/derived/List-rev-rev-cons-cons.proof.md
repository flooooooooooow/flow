# examples.verify.math.derived

*Double reverse fixes a pair cons list.*

**Source.** church — https://en.wikipedia.org/wiki/List_(abstract_data_type)

## Derived fact 1 — rev(rev(cons(x, cons(y, nil)))) = cons(x, cons(y, nil))

**Coordinate.** List · reverse · double reverse fixes pair cons · **Derived fact**

*Source: church*

*Built on: double reverse returns the list, for reverse on List*

> **Goal.** rev(rev(cons(x, cons(y, nil)))) = cons(x, cons(y, nil))
>
> $$\forall x \in \mathbb{N} \forall y \in \mathbb{N}\quad rev(rev(cons(x, cons(y, nil)))) = cons(x, cons(y, nil))$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that double reverse fixes pair cons for reverse on List. |  |  |
| ② | We invoke the derived fact governing reverse on List: double reverse returns the list, for reverse on List (instantiated for cons(x, cons(y, nil))). |  |  |
| ③ | From step 2, this implies rev(rev(cons(x, cons(y, nil)))) equals cons(x, cons(y, nil)). Hence proven. | ③ | $rev(rev(cons(x, cons(y, nil)))) = cons(x, cons(y, nil))$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ③ | step 2 |

`List · reverse · double reverse fixes pair cons`
