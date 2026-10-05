# examples.verify.math.derived

*Reverse after left-empty append preserves length.*

**Source.** church — https://en.wikipedia.org/wiki/Length_of_a_list

## Derived fact 1 — len(rev(nil ++ xs)) = len(xs)

**Coordinate.** List · length · reverse after left empty append preserves length · **Derived fact**

*Source: church*

*Built on: reverse preserves length, for length on List, empty append preserves length, for length on List*

> **Goal.** len(rev(nil ++ xs)) = len(xs)
>
> $$\forall xs \in List\quad len(rev(nil ++ xs)) = len(xs)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that reverse after left empty append preserves length for length on List. |  |  |
| ② | We invoke the derived fact governing length on List: reverse preserves length, for length on List (instantiated for nil ++ xs). |  |  |
| ③ | We invoke the derived fact governing length on List: empty append preserves length, for length on List (instantiated for xs). |  |  |
| ④ | From step 2 and step 3, this implies len(rev(nil plus plus xs)) equals len(xs). Hence proven. | ④ | $len(rev(nil ++ xs)) = len(xs)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`List · length · reverse after left empty append preserves length`
