# examples.verify.math.derived

*Appending ten singletons gives length ten.*

**Source.** church — https://en.wikipedia.org/wiki/Length_of_a_list

## Derived fact 1 — len of ten appended singletons equals 10

**Coordinate.** List · length · append of ten singletons has length ten · **Derived fact**

*Source: church*

*Built on: append preserves length sum, for length on List, append of nine singletons has length nine, for length on List*

> **Goal.** len of ten appended singletons equals 10
>
> $$\forall a \in \mathbb{N} \forall b \in \mathbb{N} \forall c \in \mathbb{N} \forall d \in \mathbb{N} \forall e \in \mathbb{N} \forall f \in \mathbb{N} \forall g \in \mathbb{N} \forall h \in \mathbb{N} \forall i \in \mathbb{N} \forall j \in \mathbb{N}\quad len(cons(a, nil) ++ cons(b, nil) ++ cons(c, nil) ++ cons(d, nil) ++ cons(e, nil) ++ cons(f, nil) ++ cons(g, nil) ++ cons(h, nil) ++ cons(i, nil) ++ cons(j, nil)) = 10$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that append of ten singletons has length ten for length on List. |  |  |
| ② | We invoke the derived fact governing length on List: append preserves length sum, for length on List (instantiated for cons(a, nil) ++ cons(b, nil) ++ cons(c, nil) ++ cons(d, nil) ++ cons(e, nil) ++ cons(f, nil) ++ cons(g, nil) ++ cons(h, nil) ++ cons(i, nil), cons(j, nil)). |  |  |
| ③ | We invoke the derived fact governing length on List: append of nine singletons has length nine, for length on List (instantiated for a, b, c, d, e, f, g, h, i). |  |  |
| ④ | From step 2 and step 3, this implies len(cons(a, nil) plus plus cons(b, nil) plus plus cons(c, nil) plus plus cons(d, nil) plus plus cons(e, nil) plus plus cons(f, nil) plus plus cons(g, nil) plus plus cons(h, nil) plus plus cons(i, nil) plus plus cons(j, nil)) equals 10. Hence proven. | ④ | $len(cons(a, nil) ++ cons(b, nil) ++ cons(c, nil) ++ cons(d, nil) ++ cons(e, nil) ++ cons(f, nil) ++ cons(g, nil) ++ cons(h, nil) ++ cons(i, nil) ++ cons(j, nil)) = 10$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`List · length · append of ten singletons has length ten`
