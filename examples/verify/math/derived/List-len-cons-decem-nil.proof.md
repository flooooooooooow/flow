# examples.verify.math.derived

*Decuple cons ending in nil has length ten.*

**Source.** church — https://en.wikipedia.org/wiki/Length_of_a_list

## Derived fact 1 — len of ten cons ending in nil equals 10

**Coordinate.** List · length · decuple cons nil has length ten · **Derived fact**

*Source: church*

*Built on: cons increases length by one, for length on List, nonuple cons nil has length nine, for length on List*

> **Goal.** len of ten cons ending in nil equals 10
>
> $$\forall a \in \mathbb{N} \forall b \in \mathbb{N} \forall c \in \mathbb{N} \forall d \in \mathbb{N} \forall e \in \mathbb{N} \forall f \in \mathbb{N} \forall g \in \mathbb{N} \forall h \in \mathbb{N} \forall i \in \mathbb{N} \forall j \in \mathbb{N}\quad len(cons(a, cons(b, cons(c, cons(d, cons(e, cons(f, cons(g, cons(h, cons(i, cons(j, nil))))))))))) = 10$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that decuple cons nil has length ten for length on List. |  |  |
| ② | We invoke the derived fact governing length on List: cons increases length by one, for length on List (instantiated for cons(b, cons(c, cons(d, cons(e, cons(f, cons(g, cons(h, cons(i, cons(j, nil)))))))))). |  |  |
| ③ | We invoke the derived fact governing length on List: nonuple cons nil has length nine, for length on List (instantiated for b, c, d, e, f, g, h, i, j). |  |  |
| ④ | From step 2 and step 3, this implies len(cons(a, cons(b, cons(c, cons(d, cons(e, cons(f, cons(g, cons(h, cons(i, cons(j, nil))))))))))) equals 10. Hence proven. | ④ | $len(cons(a, cons(b, cons(c, cons(d, cons(e, cons(f, cons(g, cons(h, cons(i, cons(j, nil))))))))))) = 10$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`List · length · decuple cons nil has length ten`
