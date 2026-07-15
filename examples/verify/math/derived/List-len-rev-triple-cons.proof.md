# examples.verify.math.derived

*Reverse preserves length of a triple cons list.*

**Source.** church — https://en.wikipedia.org/wiki/Length_of_a_list

## Derived fact 1 — len(rev(cons(a, cons(b, cons(c, nil))))) = 3

**Coordinate.** List · length · reverse of triple cons has length three · **Derived fact**

*Source: church*

*Built on: reverse preserves length, for length on List, double cons has length two, for length on List*

> **Goal.** len(rev(cons(a, cons(b, cons(c, nil))))) = 3
>
> $$\forall a \in \mathbb{N} \forall b \in \mathbb{N} \forall c \in \mathbb{N}\quad len(rev(cons(a, cons(b, cons(c, nil))))) = 3$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that reverse of triple cons has length three for length on List. |  |  |
| ② | We invoke the derived fact governing length on List: reverse preserves length, for length on List (instantiated for cons(a, cons(b, cons(c, nil)))). |  |  |
| ③ | We invoke the derived fact governing length on List: double cons has length two, for length on List (instantiated for b, c). |  |  |
| ④ | From step 2 and step 3, this implies len(rev(cons(a, cons(b, cons(c, nil))))) equals 3. Hence proven. | ④ | $len(rev(cons(a, cons(b, cons(c, nil))))) = 3$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`List · length · reverse of triple cons has length three`
