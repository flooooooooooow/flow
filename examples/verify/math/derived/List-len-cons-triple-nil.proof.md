# examples.verify.math.derived

*Triple cons ending in nil has length three.*

**Source.** church — https://en.wikipedia.org/wiki/Length_of_a_list

## Derived fact 1 — len(cons(a, cons(b, cons(c, nil)))) = 3

**Coordinate.** List · length · triple cons nil has length three · **Derived fact**

*Source: church*

*Built on: cons increases length by one, for length on List, double cons has length two, for length on List*

> **Goal.** len(cons(a, cons(b, cons(c, nil)))) = 3
>
> $$\forall a \in \mathbb{N} \forall b \in \mathbb{N} \forall c \in \mathbb{N}\quad len(cons(a, cons(b, cons(c, nil)))) = 3$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that triple cons nil has length three for length on List. |  |  |
| ② | We invoke the derived fact governing length on List: cons increases length by one, for length on List (instantiated for cons(b, cons(c, nil))). |  |  |
| ③ | We invoke the derived fact governing length on List: double cons has length two, for length on List (instantiated for b, c). |  |  |
| ④ | From step 2 and step 3, this implies len(cons(a, cons(b, cons(c, nil)))) equals 3. Hence proven. | ④ | $len(cons(a, cons(b, cons(c, nil)))) = 3$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`List · length · triple cons nil has length three`
