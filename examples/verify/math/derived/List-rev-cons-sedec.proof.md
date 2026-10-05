# examples.verify.math.derived

*Reversing a sedecuple cons list.*

**Source.** church — https://en.wikipedia.org/wiki/Reverse_(list)

## Derived fact 1 — rev of sixteen cons ending in nil reverses element order

**Coordinate.** List · reverse · reverse of sedecuple cons · **Derived fact**

*Source: church*

*Built on: reverse of cons is append of reverse tail, for reverse on List, reverse of quindecuple cons, for reverse on List*

> **Goal.** rev of sixteen cons ending in nil reverses element order
>
> $$\forall a \in \mathbb{N} \forall b \in \mathbb{N} \forall c \in \mathbb{N} \forall d \in \mathbb{N} \forall e \in \mathbb{N} \forall f \in \mathbb{N} \forall g \in \mathbb{N} \forall h \in \mathbb{N} \forall i \in \mathbb{N} \forall j \in \mathbb{N} \forall k \in \mathbb{N} \forall l \in \mathbb{N} \forall m \in \mathbb{N} \forall n \in \mathbb{N} \forall o \in \mathbb{N} \forall p \in \mathbb{N}\quad rev(cons(a, cons(b, cons(c, cons(d, cons(e, cons(f, cons(g, cons(h, cons(i, cons(j, cons(k, cons(l, cons(m, cons(n, cons(o, cons(p, nil))))))))))))))) = cons(p, cons(o, cons(n, cons(m, cons(l, cons(k, cons(j, cons(i, cons(h, cons(g, cons(f, cons(e, cons(d, cons(c, cons(b, cons(a, nil))))))))))))))))$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that reverse of sedecuple cons for reverse on List. |  |  |
| ② | We invoke the derived fact governing reverse on List: reverse of cons is append of reverse tail, for reverse on List (instantiated for a, cons(b, cons(c, cons(d, cons(e, cons(f, cons(g, cons(h, cons(i, cons(j, cons(k, cons(l, cons(m, cons(n, cons(o, cons(p, nil)))))))))))))))). |  |  |
| ③ | We invoke the derived fact governing reverse on List: reverse of quindecuple cons, for reverse on List (instantiated for b, c, d, e, f, g, h, i, j, k, l, m, n, o, p). |  |  |
| ④ | From step 2 and step 3, this implies rev(cons(a, cons(b, cons(c, cons(d, cons(e, cons(f, cons(g, cons(h, cons(i, cons(j, cons(k, cons(l, cons(m, cons(n, cons(o, cons(p, nil))))))))))))))) equals cons(p, cons(o, cons(n, cons(m, cons(l, cons(k, cons(j, cons(i, cons(h, cons(g, cons(f, cons(e, cons(d, cons(c, cons(b, cons(a, nil)))))))))))))))). Hence proven. | ④ | $rev(cons(a, cons(b, cons(c, cons(d, cons(e, cons(f, cons(g, cons(h, cons(i, cons(j, cons(k, cons(l, cons(m, cons(n, cons(o, cons(p, nil))))))))))))))) = cons(p, cons(o, cons(n, cons(m, cons(l, cons(k, cons(j, cons(i, cons(h, cons(g, cons(f, cons(e, cons(d, cons(c, cons(b, cons(a, nil))))))))))))))))$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`List · reverse · reverse of sedecuple cons`
