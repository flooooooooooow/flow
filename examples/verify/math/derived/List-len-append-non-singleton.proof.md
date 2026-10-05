# examples.verify.math.derived

*Appending nine singletons gives length nine.*

**Source.** church — https://en.wikipedia.org/wiki/Length_of_a_list

## Derived fact 1 — len of nine appended singletons equals 9

**Coordinate.** List · length · append of nine singletons has length nine · **Derived fact**

*Source: church*

*Built on: append preserves length sum, for length on List, append of eight singletons has length eight, for length on List*

> **Goal.** len of nine appended singletons equals 9
>
> $$\forall a \in \mathbb{N} \forall b \in \mathbb{N} \forall c \in \mathbb{N} \forall d \in \mathbb{N} \forall e \in \mathbb{N} \forall f \in \mathbb{N} \forall g \in \mathbb{N} \forall h \in \mathbb{N} \forall i \in \mathbb{N}\quad len(cons(a, nil) ++ cons(b, nil) ++ cons(c, nil) ++ cons(d, nil) ++ cons(e, nil) ++ cons(f, nil) ++ cons(g, nil) ++ cons(h, nil) ++ cons(i, nil)) = 9$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that append of nine singletons has length nine for length on List. |  |  |
| ② | We invoke the derived fact governing length on List: append preserves length sum, for length on List (instantiated for cons(a, nil) ++ cons(b, nil) ++ cons(c, nil) ++ cons(d, nil) ++ cons(e, nil) ++ cons(f, nil) ++ cons(g, nil) ++ cons(h, nil), cons(i, nil)). |  |  |
| ③ | We invoke the derived fact governing length on List: append of eight singletons has length eight, for length on List (instantiated for a, b, c, d, e, f, g, h). |  |  |
| ④ | From step 2 and step 3, this implies len(cons(a, nil) plus plus cons(b, nil) plus plus cons(c, nil) plus plus cons(d, nil) plus plus cons(e, nil) plus plus cons(f, nil) plus plus cons(g, nil) plus plus cons(h, nil) plus plus cons(i, nil)) equals 9. Hence proven. | ④ | $len(cons(a, nil) ++ cons(b, nil) ++ cons(c, nil) ++ cons(d, nil) ++ cons(e, nil) ++ cons(f, nil) ++ cons(g, nil) ++ cons(h, nil) ++ cons(i, nil)) = 9$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`List · length · append of nine singletons has length nine`
