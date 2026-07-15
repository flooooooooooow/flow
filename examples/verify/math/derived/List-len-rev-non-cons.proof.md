# examples.verify.math.derived

*Reverse preserves length of a nonuple cons list.*

**Source.** church — https://en.wikipedia.org/wiki/Length_of_a_list

## Derived fact 1 — len(rev(nonuple cons ending in nil)) = 9

**Coordinate.** List · length · reverse of nonuple cons has length nine · **Derived fact**

*Source: church*

*Built on: reverse preserves length, for length on List, nonuple cons nil has length nine, for length on List*

> **Goal.** len(rev(nonuple cons ending in nil)) = 9
>
> $$\forall a \in \mathbb{N} \forall b \in \mathbb{N} \forall c \in \mathbb{N} \forall d \in \mathbb{N} \forall e \in \mathbb{N} \forall f \in \mathbb{N} \forall g \in \mathbb{N} \forall h \in \mathbb{N} \forall i \in \mathbb{N}\quad len(rev(cons(a, cons(b, cons(c, cons(d, cons(e, cons(f, cons(g, cons(h, cons(i, nil))))))))))) = 9$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that reverse of nonuple cons has length nine for length on List. |  |  |
| ② | We invoke the derived fact governing length on List: reverse preserves length, for length on List (instantiated for cons(a, cons(b, cons(c, cons(d, cons(e, cons(f, cons(g, cons(h, cons(i, nil)))))))))). |  |  |
| ③ | We invoke the derived fact governing length on List: nonuple cons nil has length nine, for length on List (instantiated for a, b, c, d, e, f, g, h, i). |  |  |
| ④ | From step 2 and step 3, this implies len(rev(cons(a, cons(b, cons(c, cons(d, cons(e, cons(f, cons(g, cons(h, cons(i, nil))))))))))) equals 9. Hence proven. | ④ | $len(rev(cons(a, cons(b, cons(c, cons(d, cons(e, cons(f, cons(g, cons(h, cons(i, nil))))))))))) = 9$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`List · length · reverse of nonuple cons has length nine`
