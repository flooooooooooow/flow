# examples.verify.math.derived

*Reversing a singleton preserves length one.*

**Source.** church — https://en.wikipedia.org/wiki/Length_of_a_list

## Derived fact 1 — len(rev(cons(x, nil))) = succ(0)

**Coordinate.** List · length · reverse of singleton has length one · **Derived fact**

*Source: church*

*Built on: reverse preserves length, for length on List, singleton has length one, for length on List*

> **Goal.** len(rev(cons(x, nil))) = succ(0)
>
> $$\forall x \in \mathbb{N}\quad len(rev(cons(x, nil))) = \mathrm{succ}(0)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that reverse of singleton has length one for length on List. |  |  |
| ② | We invoke the derived fact governing length on List: reverse preserves length, for length on List (instantiated for cons(x, nil)). |  |  |
| ③ | We invoke the derived fact governing length on List: singleton has length one, for length on List (instantiated for x). |  |  |
| ④ | From step 2 and step 3, this implies len(rev(cons(x, nil))) equals the successor of 0. Hence proven. | ④ | $len(rev(cons(x, nil))) = \mathrm{succ}(0)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`List · length · reverse of singleton has length one`
