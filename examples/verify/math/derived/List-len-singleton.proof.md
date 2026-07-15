# examples.verify.math.derived

*A singleton list has length one.*

**Source.** church — https://en.wikipedia.org/wiki/Length_of_a_list

## Derived fact 1 — len(cons(x, nil)) = succ(0)

**Coordinate.** List · length · singleton has length one · **Derived fact**

*Source: church*

*Built on: cons increases length by one, for length on List, the empty list has length zero, for length on List*

> **Goal.** len(cons(x, nil)) = succ(0)
>
> $$\forall x \in \mathbb{N}\quad len(cons(x, nil)) = \mathrm{succ}(0)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that singleton has length one for length on List. |  |  |
| ② | We invoke the derived fact governing length on List: cons increases length by one, for length on List (instantiated for x, nil). |  |  |
| ③ | We invoke the derived fact governing length on List: the empty list has length zero, for length on List. |  |  |
| ④ | From step 2 and step 3, this implies len(cons(x, nil)) equals the successor of 0. Hence proven. | ④ | $len(cons(x, nil)) = \mathrm{succ}(0)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`List · length · singleton has length one`
