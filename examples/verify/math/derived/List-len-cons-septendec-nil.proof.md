# examples.verify.math.derived

*Septendecuple cons ending in nil has length seventeen.*

**Source.** church — https://en.wikipedia.org/wiki/Length_of_a_list

## Derived fact 1 — len of seventeen cons ending in nil equals 17

**Coordinate.** List · length · septendecuple cons nil has length seventeen · **Derived fact**

*Source: church*

*Built on: cons increases length by one, for length on List, sedecuple cons nil has length sixteen, for length on List*

> **Goal.** len of seventeen cons ending in nil equals 17
>
> $$\forall a \in \mathbb{N} \forall b \in \mathbb{N} \forall c \in \mathbb{N} \forall d \in \mathbb{N} \forall e \in \mathbb{N} \forall f \in \mathbb{N} \forall g \in \mathbb{N} \forall h \in \mathbb{N} \forall i \in \mathbb{N} \forall j \in \mathbb{N} \forall k \in \mathbb{N} \forall l \in \mathbb{N} \forall m \in \mathbb{N} \forall n \in \mathbb{N} \forall o \in \mathbb{N} \forall p \in \mathbb{N} \forall q \in \mathbb{N}\quad len(cons(a, cons(b, cons(c, cons(d, cons(e, cons(f, cons(g, cons(h, cons(i, cons(j, cons(k, cons(l, cons(m, cons(n, cons(o, cons(p, cons(q, nil)))))))))))))))) = 17$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that septendecuple cons nil has length seventeen for length on List. |  |  |
| ② | We invoke the derived fact governing length on List: cons increases length by one, for length on List (instantiated for cons(b, cons(c, cons(d, cons(e, cons(f, cons(g, cons(h, cons(i, cons(j, cons(k, cons(l, cons(m, cons(n, cons(o, cons(p, cons(q, nil))))))))))))))))). |  |  |
| ③ | We invoke the derived fact governing length on List: sedecuple cons nil has length sixteen, for length on List (instantiated for b, c, d, e, f, g, h, i, j, k, l, m, n, o, p, q). |  |  |
| ④ | From step 2 and step 3, this implies len(cons(a, cons(b, cons(c, cons(d, cons(e, cons(f, cons(g, cons(h, cons(i, cons(j, cons(k, cons(l, cons(m, cons(n, cons(o, cons(p, cons(q, nil)))))))))))))))) equals 17. Hence proven. | ④ | $len(cons(a, cons(b, cons(c, cons(d, cons(e, cons(f, cons(g, cons(h, cons(i, cons(j, cons(k, cons(l, cons(m, cons(n, cons(o, cons(p, cons(q, nil)))))))))))))))) = 17$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`List · length · septendecuple cons nil has length seventeen`
