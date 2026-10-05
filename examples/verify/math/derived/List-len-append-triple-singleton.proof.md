# examples.verify.math.derived

*Appending three singletons gives length three.*

**Source.** church — https://en.wikipedia.org/wiki/Length_of_a_list

## Derived fact 1 — len(cons(a, nil) ++ cons(b, nil) ++ cons(c, nil)) = 3

**Coordinate.** List · length · append of three singletons has length three · **Derived fact**

*Source: church*

*Built on: append preserves length sum, for length on List, append of two singletons has length two, for length on List*

> **Goal.** len(cons(a, nil) ++ cons(b, nil) ++ cons(c, nil)) = 3
>
> $$\forall a \in \mathbb{N} \forall b \in \mathbb{N} \forall c \in \mathbb{N}\quad len(cons(a, nil) ++ cons(b, nil) ++ cons(c, nil)) = 3$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that append of three singletons has length three for length on List. |  |  |
| ② | We invoke the derived fact governing length on List: append preserves length sum, for length on List (instantiated for cons(a, nil) ++ cons(b, nil), cons(c, nil)). |  |  |
| ③ | We invoke the derived fact governing length on List: append of two singletons has length two, for length on List (instantiated for a, b). |  |  |
| ④ | From step 2 and step 3, this implies len(cons(a, nil) plus plus cons(b, nil) plus plus cons(c, nil)) equals 3. Hence proven. | ④ | $len(cons(a, nil) ++ cons(b, nil) ++ cons(c, nil)) = 3$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`List · length · append of three singletons has length three`
