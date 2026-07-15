# examples.verify.math.derived

*A singleton list is fixed by reverse.*

**Source.** church — https://en.wikipedia.org/wiki/List_(abstract_data_type)

## Derived fact 1 — rev(cons(x, nil)) = cons(x, nil)

**Coordinate.** List · reverse · singleton reverse is identity · **Derived fact**

*Source: church*

*Built on: singleton is fixed by reverse, for reverse on List*

> **Goal.** rev(cons(x, nil)) = cons(x, nil)
>
> $$\forall x \in \mathbb{N}\quad rev(cons(x, nil)) = cons(x, nil)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that singleton reverse is identity for reverse on List. |  |  |
| ② | We invoke the derived fact governing reverse on List: singleton is fixed by reverse, for reverse on List (instantiated for x). |  |  |
| ③ | From step 2, this implies rev(cons(x, nil)) equals cons(x, nil). Hence proven. | ③ | $rev(cons(x, nil)) = cons(x, nil)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ③ | step 2 |

`List · reverse · singleton reverse is identity`
