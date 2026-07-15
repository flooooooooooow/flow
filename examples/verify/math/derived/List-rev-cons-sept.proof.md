# examples.verify.math.derived

*Reversing a septuple cons list.*

**Source.** church — https://en.wikipedia.org/wiki/Reverse_(list)

## Derived fact 1 — rev(cons(a, cons(b, cons(c, cons(d, cons(e, cons(f, cons(g, nil))))))) = cons(g, cons(f, cons(e, cons(d, cons(c, cons(b, cons(a, nil)))))))

**Coordinate.** List · reverse · reverse of septuple cons · **Derived fact**

*Source: church*

*Built on: reverse of cons is append of reverse tail, for reverse on List, reverse of sextuple cons, for reverse on List*

> **Goal.** rev(cons(a, cons(b, cons(c, cons(d, cons(e, cons(f, cons(g, nil))))))) = cons(g, cons(f, cons(e, cons(d, cons(c, cons(b, cons(a, nil)))))))
>
> $$\forall a \in \mathbb{N} \forall b \in \mathbb{N} \forall c \in \mathbb{N} \forall d \in \mathbb{N} \forall e \in \mathbb{N} \forall f \in \mathbb{N} \forall g \in \mathbb{N}\quad rev(cons(a, cons(b, cons(c, cons(d, cons(e, cons(f, cons(g, nil))))))) = cons(g, cons(f, cons(e, cons(d, cons(c, cons(b, cons(a, nil)))))))$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that reverse of septuple cons for reverse on List. |  |  |
| ② | We invoke the derived fact governing reverse on List: reverse of cons is append of reverse tail, for reverse on List (instantiated for a, cons(b, cons(c, cons(d, cons(e, cons(f, cons(g, nil))))))). |  |  |
| ③ | We invoke the derived fact governing reverse on List: reverse of sextuple cons, for reverse on List (instantiated for b, c, d, e, f, g). |  |  |
| ④ | From step 2 and step 3, this implies rev(cons(a, cons(b, cons(c, cons(d, cons(e, cons(f, cons(g, nil))))))) equals cons(g, cons(f, cons(e, cons(d, cons(c, cons(b, cons(a, nil))))))). Hence proven. | ④ | $rev(cons(a, cons(b, cons(c, cons(d, cons(e, cons(f, cons(g, nil))))))) = cons(g, cons(f, cons(e, cons(d, cons(c, cons(b, cons(a, nil)))))))$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`List · reverse · reverse of septuple cons`
