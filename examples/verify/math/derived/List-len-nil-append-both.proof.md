# examples.verify.math.derived

*Empty append on both sides preserves zero length.*

**Source.** church — https://en.wikipedia.org/wiki/Length_of_a_list

## Derived fact 1 — len(nil ++ nil) = 0

**Coordinate.** List · length · double empty append has length zero · **Derived fact**

*Source: church*

*Built on: empty append preserves length, for length on List, the empty list has length zero, for length on List*

> **Goal.** len(nil ++ nil) = 0
>
> $$len(nil ++ nil) = 0$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that double empty append has length zero for length on List. |  |  |
| ② | We invoke the derived fact governing length on List: empty append preserves length, for length on List (instantiated for nil). |  |  |
| ③ | We invoke the derived fact governing length on List: the empty list has length zero, for length on List. |  |  |
| ④ | From step 2 and step 3, this implies len(nil plus plus nil) equals 0. Hence proven. | ④ | $len(nil ++ nil) = 0$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`List · length · double empty append has length zero`
