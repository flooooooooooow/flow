# examples.verify.math.derived

*Reverse preserves length of a quattuordecuple cons list.*

**Source.** church — https://en.wikipedia.org/wiki/Length_of_a_list

## Derived fact 1 — len(rev(quattuordecuple cons ending in nil)) = 14

**Coordinate.** List · length · reverse of quattuordecuple cons has length fourteen · **Derived fact**

*Source: church*

*Built on: reverse preserves length, for length on List, quattuordecuple cons nil has length fourteen, for length on List*

> **Goal.** len(rev(quattuordecuple cons ending in nil)) = 14
>
> $$\forall a \in \mathbb{N} \forall b \in \mathbb{N} \forall c \in \mathbb{N} \forall d \in \mathbb{N} \forall e \in \mathbb{N} \forall f \in \mathbb{N} \forall g \in \mathbb{N} \forall h \in \mathbb{N} \forall i \in \mathbb{N} \forall j \in \mathbb{N} \forall k \in \mathbb{N} \forall l \in \mathbb{N} \forall m \in \mathbb{N} \forall n \in \mathbb{N}\quad len(rev(cons(a, cons(b, cons(c, cons(d, cons(e, cons(f, cons(g, cons(h, cons(i, cons(j, cons(k, cons(l, cons(m, cons(n, nil))))))))))))))) = 14$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that reverse of quattuordecuple cons has length fourteen for length on List. |  |  |
| ② | We invoke the derived fact governing length on List: reverse preserves length, for length on List (instantiated for cons(a, cons(b, cons(c, cons(d, cons(e, cons(f, cons(g, cons(h, cons(i, cons(j, cons(k, cons(l, cons(m, cons(n, nil)))))))))))))). |  |  |
| ③ | We invoke the derived fact governing length on List: quattuordecuple cons nil has length fourteen, for length on List (instantiated for a, b, c, d, e, f, g, h, i, j, k, l, m, n). |  |  |
| ④ | From step 2 and step 3, this implies len(rev(cons(a, cons(b, cons(c, cons(d, cons(e, cons(f, cons(g, cons(h, cons(i, cons(j, cons(k, cons(l, cons(m, cons(n, nil))))))))))))))) equals 14. Hence proven. | ④ | $len(rev(cons(a, cons(b, cons(c, cons(d, cons(e, cons(f, cons(g, cons(h, cons(i, cons(j, cons(k, cons(l, cons(m, cons(n, nil))))))))))))))) = 14$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`List · length · reverse of quattuordecuple cons has length fourteen`
