# examples.verify.math.derived

*Appending seven singletons gives length seven.*

**Source.** church — https://en.wikipedia.org/wiki/Length_of_a_list

## Derived fact 1 — len of seven appended singletons equals 7

**Coordinate.** List · length · append of seven singletons has length seven · **Derived fact**

*Source: church*

*Built on: append preserves length sum, for length on List, append of six singletons has length six, for length on List*

> **Goal.** len of seven appended singletons equals 7
>
> $$\forall a \in \mathbb{N} \forall b \in \mathbb{N} \forall c \in \mathbb{N} \forall d \in \mathbb{N} \forall e \in \mathbb{N} \forall f \in \mathbb{N} \forall g \in \mathbb{N}\quad len(cons(a, nil) ++ cons(b, nil) ++ cons(c, nil) ++ cons(d, nil) ++ cons(e, nil) ++ cons(f, nil) ++ cons(g, nil)) = 7$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that append of seven singletons has length seven for length on List. |  |  |
| ② | We invoke the derived fact governing length on List: append preserves length sum, for length on List (instantiated for cons(a, nil) ++ cons(b, nil) ++ cons(c, nil) ++ cons(d, nil) ++ cons(e, nil) ++ cons(f, nil), cons(g, nil)). |  |  |
| ③ | We invoke the derived fact governing length on List: append of six singletons has length six, for length on List (instantiated for a, b, c, d, e, f). |  |  |
| ④ | From step 2 and step 3, this implies len(cons(a, nil) plus plus cons(b, nil) plus plus cons(c, nil) plus plus cons(d, nil) plus plus cons(e, nil) plus plus cons(f, nil) plus plus cons(g, nil)) equals 7. Hence proven. | ④ | $len(cons(a, nil) ++ cons(b, nil) ++ cons(c, nil) ++ cons(d, nil) ++ cons(e, nil) ++ cons(f, nil) ++ cons(g, nil)) = 7$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`List · length · append of seven singletons has length seven`
