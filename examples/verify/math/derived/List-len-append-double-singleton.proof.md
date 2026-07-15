# examples.verify.math.derived

*Appending two singletons increases length by two.*

**Source.** church — https://en.wikipedia.org/wiki/Length_of_a_list

## Derived fact 1 — len(cons(a, nil) ++ cons(b, nil)) = 2

**Coordinate.** List · length · append of two singletons has length two · **Derived fact**

*Source: church*

*Built on: append preserves length sum, for length on List, singleton has length one, for length on List*

> **Goal.** len(cons(a, nil) ++ cons(b, nil)) = 2
>
> $$\forall a \in \mathbb{N} \forall b \in \mathbb{N}\quad len(cons(a, nil) ++ cons(b, nil)) = 2$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that append of two singletons has length two for length on List. |  |  |
| ② | We invoke the derived fact governing length on List: append preserves length sum, for length on List (instantiated for cons(a, nil), cons(b, nil)). |  |  |
| ③ | We invoke the derived fact governing length on List: singleton has length one, for length on List (instantiated for a). |  |  |
| ④ | We invoke the derived fact governing length on List: singleton has length one, for length on List (instantiated for b). |  |  |
| ⑤ | From step 2, step 3, and step 4, this implies len(cons(a, nil) plus plus cons(b, nil)) equals 2. Hence proven. | ⑤ | $len(cons(a, nil) ++ cons(b, nil)) = 2$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ⑤ | step 2, step 3, and step 4 |

`List · length · append of two singletons has length two`
