# examples.verify.math.derived

*Reverse preserves length of a duodecuple cons list.*

**Source.** church — https://en.wikipedia.org/wiki/Length_of_a_list

## Derived fact 1 — len(rev(duodecuple cons ending in nil)) = 12

**Coordinate.** List · length · reverse of duodecuple cons has length twelve · **Derived fact**

*Source: church*

*Built on: reverse preserves length, for length on List, duodecuple cons nil has length twelve, for length on List*

> **Goal.** len(rev(duodecuple cons ending in nil)) = 12
>
> $$\forall a \in \mathbb{N} \forall b \in \mathbb{N} \forall c \in \mathbb{N} \forall d \in \mathbb{N} \forall e \in \mathbb{N} \forall f \in \mathbb{N} \forall g \in \mathbb{N} \forall h \in \mathbb{N} \forall i \in \mathbb{N} \forall j \in \mathbb{N} \forall k \in \mathbb{N} \forall l \in \mathbb{N}\quad len(rev(cons(a, cons(b, cons(c, cons(d, cons(e, cons(f, cons(g, cons(h, cons(i, cons(j, cons(k, cons(l, nil))))))))))))) = 12$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that reverse of duodecuple cons has length twelve for length on List. |  |  |
| ② | We invoke the derived fact governing length on List: reverse preserves length, for length on List (instantiated for cons(a, cons(b, cons(c, cons(d, cons(e, cons(f, cons(g, cons(h, cons(i, cons(j, cons(k, cons(l, nil)))))))))))). |  |  |
| ③ | We invoke the derived fact governing length on List: duodecuple cons nil has length twelve, for length on List (instantiated for a, b, c, d, e, f, g, h, i, j, k, l). |  |  |
| ④ | From step 2 and step 3, this implies len(rev(cons(a, cons(b, cons(c, cons(d, cons(e, cons(f, cons(g, cons(h, cons(i, cons(j, cons(k, cons(l, nil))))))))))))) equals 12. Hence proven. | ④ | $len(rev(cons(a, cons(b, cons(c, cons(d, cons(e, cons(f, cons(g, cons(h, cons(i, cons(j, cons(k, cons(l, nil))))))))))))) = 12$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`List · length · reverse of duodecuple cons has length twelve`
