# examples.verify.math.derived

*Reversing a two-element cons list swaps endpoints.*

**Source.** church — https://en.wikipedia.org/wiki/List_(abstract_data_type)

## Derived fact 1 — rev(cons(x, cons(y, nil))) = cons(y, cons(x, nil))

**Coordinate.** List · reverse · reverse of pair cons swaps endpoints · **Derived fact**

*Source: church*

*Built on: reverse of cons appends reversed tail, for reverse on List, singleton reverse is identity, for reverse on List*

> **Goal.** rev(cons(x, cons(y, nil))) = cons(y, cons(x, nil))
>
> $$\forall x \in \mathbb{N} \forall y \in \mathbb{N}\quad rev(cons(x, cons(y, nil))) = cons(y, cons(x, nil))$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that reverse of pair cons swaps endpoints for reverse on List. |  |  |
| ② | We invoke the derived fact governing reverse on List: reverse of cons appends reversed tail, for reverse on List (instantiated for x, cons(y, nil)). |  |  |
| ③ | We invoke the derived fact governing reverse on List: singleton reverse is identity, for reverse on List (instantiated for y). |  |  |
| ④ | From step 2 and step 3, this implies rev(cons(x, cons(y, nil))) equals cons(y, cons(x, nil)). Hence proven. | ④ | $rev(cons(x, cons(y, nil))) = cons(y, cons(x, nil))$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`List · reverse · reverse of pair cons swaps endpoints`
