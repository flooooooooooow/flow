# examples.verify.math.derived

*Appending to the empty list preserves length.*

**Source.** church — https://en.wikipedia.org/wiki/Length_of_a_list

## Derived fact 1 — len(nil ++ xs) = len(xs)

**Coordinate.** List · length · empty append preserves length · **Derived fact**

*Source: church*

*Built on: length adds under append, for length on List, adding zero on the left does not change the number*

> **Goal.** len(nil ++ xs) = len(xs)
>
> $$\forall xs \in List\quad len(nil ++ xs) = len(xs)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that empty append preserves length for length on List. |  |  |
| ② | We invoke the derived fact governing length on List: length adds under append, for length on List (instantiated for nil, xs). |  |  |
| ③ | We invoke the definitional clause governing addition on the natural numbers: adding zero on the left does not change the number (instantiated for len(xs)). | ③ | $0 + len(xs) = len(xs)$ |
| ④ | From step 2 and step 3, this implies len(nil plus plus xs) equals len(xs). Hence proven. | ④ | $len(nil ++ xs) = len(xs)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`List · length · empty append preserves length`
