# examples.verify.math.derived

*Reverse of cons preserves the tail length increment.*

**Source.** church — https://en.wikipedia.org/wiki/Length_of_a_list

## Derived fact 1 — len(rev(cons(x, xs))) = len(cons(x, xs))

**Coordinate.** List · length · reverse preserves cons length derived · **Derived fact**

*Source: church*

*Built on: reverse preserves cons length, for length on List*

> **Goal.** len(rev(cons(x, xs))) = len(cons(x, xs))
>
> $$\forall x \in \mathbb{N} \forall xs \in List\quad len(rev(cons(x, xs))) = len(cons(x, xs))$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that reverse preserves cons length derived for length on List. |  |  |
| ② | We invoke the derived fact governing length on List: reverse preserves cons length, for length on List (instantiated for x, xs). |  |  |
| ③ | From step 2, this implies len(rev(cons(x, xs))) equals len(cons(x, xs)). Hence proven. | ③ | $len(rev(cons(x, xs))) = len(cons(x, xs))$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ③ | step 2 |

`List · length · reverse preserves cons length derived`
