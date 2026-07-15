# examples.verify.math.derived

*The empty list has length zero.*

**Source.** church — https://en.wikipedia.org/wiki/Length_of_a_list

## Derived fact 1 — len(nil) = 0

**Coordinate.** List · length · the empty list has length zero · **Derived fact**

*Source: church*

*Built on: empty is the left identity, for append on List, adding zero on the left does not change the number*

> **Goal.** len(nil) = 0
>
> $$len(nil) = 0$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that the empty list has length zero for length on List. |  |  |
| ② | We invoke the definitional clause governing append on List: empty is the left identity, for append on List (instantiated for nil). |  |  |
| ③ | We invoke the definitional clause governing addition on the natural numbers: adding zero on the left does not change the number (instantiated for 0). | ③ | $0 + 0 = 0$ |
| ④ | From step 2 and step 3, this implies len(nil) equals 0. Hence proven. | ④ | $len(nil) = 0$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`List · length · the empty list has length zero`
