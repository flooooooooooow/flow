# examples.verify.math.derived

*Double reverse restores a tredecuple cons list.*

**Source.** church — https://en.wikipedia.org/wiki/Reverse_(list)

## Derived fact 1 — rev(rev(tredecuple cons with tail xs)) = tredecuple cons with tail xs

**Coordinate.** List · reverse · double reverse of tredecuple cons · **Derived fact**

*Source: church*

*Built on: reverse is an involution, for reverse on List*

> **Goal.** rev(rev(tredecuple cons with tail xs)) = tredecuple cons with tail xs
>
> $$\forall a \in \mathbb{N} \forall b \in \mathbb{N} \forall c \in \mathbb{N} \forall d \in \mathbb{N} \forall e \in \mathbb{N} \forall f \in \mathbb{N} \forall g \in \mathbb{N} \forall h \in \mathbb{N} \forall i \in \mathbb{N} \forall j \in \mathbb{N} \forall k \in \mathbb{N} \forall l \in \mathbb{N} \forall m \in \mathbb{N} \forall xs \in List\quad rev(rev(cons(a, cons(b, cons(c, cons(d, cons(e, cons(f, cons(g, cons(h, cons(i, cons(j, cons(k, cons(l, cons(m, xs))))))))))))))) = cons(a, cons(b, cons(c, cons(d, cons(e, cons(f, cons(g, cons(h, cons(i, cons(j, cons(k, cons(l, cons(m, xs))))))))))))))$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that double reverse of tredecuple cons for reverse on List. |  |  |
| ② | We invoke the derived fact governing reverse on List: reverse is an involution, for reverse on List (instantiated for cons(a, cons(b, cons(c, cons(d, cons(e, cons(f, cons(g, cons(h, cons(i, cons(j, cons(k, cons(l, cons(m, xs)))))))))))))). |  |  |
| ③ | From step 2, this implies rev(rev(cons(a, cons(b, cons(c, cons(d, cons(e, cons(f, cons(g, cons(h, cons(i, cons(j, cons(k, cons(l, cons(m, xs))))))))))))))) equals cons(a, cons(b, cons(c, cons(d, cons(e, cons(f, cons(g, cons(h, cons(i, cons(j, cons(k, cons(l, cons(m, xs)))))))))))))). Hence proven. | ③ | $rev(rev(cons(a, cons(b, cons(c, cons(d, cons(e, cons(f, cons(g, cons(h, cons(i, cons(j, cons(k, cons(l, cons(m, xs))))))))))))))) = cons(a, cons(b, cons(c, cons(d, cons(e, cons(f, cons(g, cons(h, cons(i, cons(j, cons(k, cons(l, cons(m, xs))))))))))))))$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ③ | step 2 |

`List · reverse · double reverse of tredecuple cons`
