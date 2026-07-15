# examples.verify.math.derived

*Double reverse of nil has length zero.*

**Source.** church — https://en.wikipedia.org/wiki/Length_of_a_list

## Derived fact 1 — len(rev(rev(nil))) = 0

**Coordinate.** List · length · double reverse of nil has length zero · **Derived fact**

*Source: church*

*Built on: reverse preserves length, for length on List, empty list has length zero, for length on List*

> **Goal.** len(rev(rev(nil))) = 0
>
> $$len(rev(rev(nil))) = 0$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that double reverse of nil has length zero for length on List. |  |  |
| ② | We invoke the derived fact governing length on List: reverse preserves length, for length on List (instantiated for nil). |  |  |
| ③ | We invoke the derived fact governing length on List: empty list has length zero, for length on List. |  |  |
| ④ | From step 2 and step 3, this implies len(rev(rev(nil))) equals 0. Hence proven. | ④ | $len(rev(rev(nil))) = 0$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`List · length · double reverse of nil has length zero`
