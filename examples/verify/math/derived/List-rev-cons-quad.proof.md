# examples.verify.math.derived

*Reversing a quadruple cons list.*

**Source.** church — https://en.wikipedia.org/wiki/Reverse_(list)

## Derived fact 1 — rev(cons(a, cons(b, cons(c, cons(d, nil))))) = cons(d, cons(c, cons(b, cons(a, nil))))

**Coordinate.** List · reverse · reverse of quadruple cons · **Derived fact**

*Source: church*

*Built on: reverse of cons is append of reverse tail, for reverse on List, reverse of triple cons, for reverse on List*

> **Goal.** rev(cons(a, cons(b, cons(c, cons(d, nil))))) = cons(d, cons(c, cons(b, cons(a, nil))))
>
> $$\forall a \in \mathbb{N} \forall b \in \mathbb{N} \forall c \in \mathbb{N} \forall d \in \mathbb{N}\quad rev(cons(a, cons(b, cons(c, cons(d, nil))))) = cons(d, cons(c, cons(b, cons(a, nil))))$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that reverse of quadruple cons for reverse on List. |  |  |
| ② | We invoke the derived fact governing reverse on List: reverse of cons is append of reverse tail, for reverse on List (instantiated for a, cons(b, cons(c, cons(d, nil)))). |  |  |
| ③ | We invoke the derived fact governing reverse on List: reverse of triple cons, for reverse on List (instantiated for b, c, d). |  |  |
| ④ | From step 2 and step 3, this implies rev(cons(a, cons(b, cons(c, cons(d, nil))))) equals cons(d, cons(c, cons(b, cons(a, nil)))). Hence proven. | ④ | $rev(cons(a, cons(b, cons(c, cons(d, nil))))) = cons(d, cons(c, cons(b, cons(a, nil))))$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`List · reverse · reverse of quadruple cons`
