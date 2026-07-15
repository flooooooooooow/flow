# examples.verify.math.derived

*Reverse preserves length for cons lists.*

**Source.** church — https://en.wikipedia.org/wiki/Length_of_a_list

## Derived fact 1 — len(rev(cons(x, xs))) = len(cons(x, xs))

**Coordinate.** List · length · reverse preserves cons length · **Derived fact**

*Source: church*

*Built on: reverse preserves length, for length on List, cons increases length by one, for length on List*

> **Goal.** len(rev(cons(x, xs))) = len(cons(x, xs))
>
> $$\forall x \in \mathbb{N} \forall xs \in List\quad len(rev(cons(x, xs))) = len(cons(x, xs))$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that reverse preserves cons length for length on List. |  |  |
| ② | We invoke the derived fact governing length on List: reverse preserves length, for length on List (instantiated for cons(x, xs)). |  |  |
| ③ | We invoke the derived fact governing length on List: cons increases length by one, for length on List (instantiated for x, xs). |  |  |
| ④ | From step 2 and step 3, this implies len(rev(cons(x, xs))) equals len(cons(x, xs)). Hence proven. | ④ | $len(rev(cons(x, xs))) = len(cons(x, xs))$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`List · length · reverse preserves cons length`
