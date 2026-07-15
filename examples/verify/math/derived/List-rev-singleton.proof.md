# examples.verify.math.derived

*A singleton list is fixed by reverse.*

**Source.** church — https://en.wikipedia.org/wiki/List_(abstract_data_type)

## Derived fact 1 — rev(cons(x, nil)) = cons(x, nil)

**Coordinate.** List · reverse · singleton is fixed by reverse · **Derived fact**

*Source: church*

*Built on: reverse of cons appends reversed tail, for reverse on List, reversing empty yields empty, for reverse on List*

> **Goal.** rev(cons(x, nil)) = cons(x, nil)
>
> $$\forall x \in \mathbb{N}\quad rev(cons(x, nil)) = cons(x, nil)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that singleton is fixed by reverse for reverse on List. |  |  |
| ② | We invoke the derived fact governing reverse on List: reverse of cons appends reversed tail, for reverse on List (instantiated for x, nil). |  |  |
| ③ | We invoke the derived fact governing reverse on List: reversing empty yields empty, for reverse on List. |  |  |
| ④ | From step 2 and step 3, this implies rev(cons(x, nil)) equals cons(x, nil). Hence proven. | ④ | $rev(cons(x, nil)) = cons(x, nil)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`List · reverse · singleton is fixed by reverse`
