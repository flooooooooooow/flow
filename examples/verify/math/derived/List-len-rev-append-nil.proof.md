# examples.verify.math.derived

*Reverse length is preserved after right-empty append.*

**Source.** church — https://en.wikipedia.org/wiki/Length_of_a_list

## Derived fact 1 — len(rev(xs ++ nil)) = len(xs)

**Coordinate.** List · length · reverse after right empty append preserves length · **Derived fact**

*Source: church*

*Built on: reverse preserves length, for length on List, append empty on the right preserves length, for length on List*

> **Goal.** len(rev(xs ++ nil)) = len(xs)
>
> $$\forall xs \in List\quad len(rev(xs ++ nil)) = len(xs)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that reverse after right empty append preserves length for length on List. |  |  |
| ② | We invoke the derived fact governing length on List: reverse preserves length, for length on List (instantiated for xs ++ nil). |  |  |
| ③ | We invoke the derived fact governing length on List: append empty on the right preserves length, for length on List (instantiated for xs). |  |  |
| ④ | From step 2 and step 3, this implies len(rev(xs plus plus nil)) equals len(xs). Hence proven. | ④ | $len(rev(xs ++ nil)) = len(xs)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`List · length · reverse after right empty append preserves length`
