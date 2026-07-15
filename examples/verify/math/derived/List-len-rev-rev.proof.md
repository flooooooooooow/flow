# examples.verify.math.derived

*Double reverse preserves length.*

**Source.** church — https://en.wikipedia.org/wiki/Length_of_a_list

## Derived fact 1 — len(rev(rev(xs))) = len(xs)

**Coordinate.** List · length · double reverse preserves length · **Derived fact**

*Source: church*

*Built on: reverse preserves length, for length on List, double reverse returns the list, for reverse on List*

> **Goal.** len(rev(rev(xs))) = len(xs)
>
> $$\forall xs \in List\quad len(rev(rev(xs))) = len(xs)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that double reverse preserves length for length on List. |  |  |
| ② | We invoke the derived fact governing length on List: reverse preserves length, for length on List (instantiated for rev(xs)). |  |  |
| ③ | We invoke the derived fact governing reverse on List: double reverse returns the list, for reverse on List (instantiated for xs). |  |  |
| ④ | From step 2 and step 3, this implies len(rev(rev(xs))) equals len(xs). Hence proven. | ④ | $len(rev(rev(xs))) = len(xs)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`List · length · double reverse preserves length`
