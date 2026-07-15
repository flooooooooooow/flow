# examples.verify.math.derived

*Reverse preserves length of a quindecuple cons list.*

**Source.** church — https://en.wikipedia.org/wiki/Length_of_a_list

## Derived fact 1 — len(rev(quindecuple cons ending in nil)) = 15

**Coordinate.** List · length · reverse of quindecuple cons has length fifteen · **Derived fact**

*Source: church*

*Built on: reverse preserves length, for length on List, quindecuple cons nil has length fifteen, for length on List*

> **Goal.** len(rev(quindecuple cons ending in nil)) = 15
>
> $$\forall a \in \mathbb{N} \forall b \in \mathbb{N} \forall c \in \mathbb{N} \forall d \in \mathbb{N} \forall e \in \mathbb{N} \forall f \in \mathbb{N} \forall g \in \mathbb{N} \forall h \in \mathbb{N} \forall i \in \mathbb{N} \forall j \in \mathbb{N} \forall k \in \mathbb{N} \forall l \in \mathbb{N} \forall m \in \mathbb{N} \forall n \in \mathbb{N} \forall o \in \mathbb{N}\quad len(rev(cons(a, cons(b, cons(c, cons(d, cons(e, cons(f, cons(g, cons(h, cons(i, cons(j, cons(k, cons(l, cons(m, cons(n, cons(o, nil))))))))))))))) = 15$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that reverse of quindecuple cons has length fifteen for length on List. |  |  |
| ② | We invoke the derived fact governing length on List: reverse preserves length, for length on List (instantiated for cons(a, cons(b, cons(c, cons(d, cons(e, cons(f, cons(g, cons(h, cons(i, cons(j, cons(k, cons(l, cons(m, cons(n, cons(o, nil))))))))))))))). |  |  |
| ③ | We invoke the derived fact governing length on List: quindecuple cons nil has length fifteen, for length on List (instantiated for a, b, c, d, e, f, g, h, i, j, k, l, m, n, o). |  |  |
| ④ | From step 2 and step 3, this implies len(rev(cons(a, cons(b, cons(c, cons(d, cons(e, cons(f, cons(g, cons(h, cons(i, cons(j, cons(k, cons(l, cons(m, cons(n, cons(o, nil))))))))))))))) equals 15. Hence proven. | ④ | $len(rev(cons(a, cons(b, cons(c, cons(d, cons(e, cons(f, cons(g, cons(h, cons(i, cons(j, cons(k, cons(l, cons(m, cons(n, cons(o, nil))))))))))))))) = 15$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`List · length · reverse of quindecuple cons has length fifteen`
