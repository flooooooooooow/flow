# examples.verify.math.derived

*Reverse preserves length of a decuple cons list.*

**Source.** church — https://en.wikipedia.org/wiki/Length_of_a_list

## Derived fact 1 — len(rev(decuple cons ending in nil)) = 10

**Coordinate.** List · length · reverse of decuple cons has length ten · **Derived fact**

*Source: church*

*Built on: reverse preserves length, for length on List, decuple cons nil has length ten, for length on List*

> **Goal.** len(rev(decuple cons ending in nil)) = 10
>
> $$\forall a \in \mathbb{N} \forall b \in \mathbb{N} \forall c \in \mathbb{N} \forall d \in \mathbb{N} \forall e \in \mathbb{N} \forall f \in \mathbb{N} \forall g \in \mathbb{N} \forall h \in \mathbb{N} \forall i \in \mathbb{N} \forall j \in \mathbb{N}\quad len(rev(cons(a, cons(b, cons(c, cons(d, cons(e, cons(f, cons(g, cons(h, cons(i, cons(j, nil)))))))))))) = 10$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that reverse of decuple cons has length ten for length on List. |  |  |
| ② | We invoke the derived fact governing length on List: reverse preserves length, for length on List (instantiated for cons(a, cons(b, cons(c, cons(d, cons(e, cons(f, cons(g, cons(h, cons(i, cons(j, nil))))))))))). |  |  |
| ③ | We invoke the derived fact governing length on List: decuple cons nil has length ten, for length on List (instantiated for a, b, c, d, e, f, g, h, i, j). |  |  |
| ④ | From step 2 and step 3, this implies len(rev(cons(a, cons(b, cons(c, cons(d, cons(e, cons(f, cons(g, cons(h, cons(i, cons(j, nil)))))))))))) equals 10. Hence proven. | ④ | $len(rev(cons(a, cons(b, cons(c, cons(d, cons(e, cons(f, cons(g, cons(h, cons(i, cons(j, nil)))))))))))) = 10$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`List · length · reverse of decuple cons has length ten`
