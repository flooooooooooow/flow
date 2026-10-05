# examples.verify.math.derived

*Appending the empty list on the right preserves length.*

**Source.** church — https://en.wikipedia.org/wiki/Length_of_a_list

## Derived fact 1 — len(xs ++ nil) = len(xs)

**Coordinate.** List · length · append empty on the right preserves length · **Derived fact**

*Source: church*

*Built on: length adds under append, for length on List, adding zero on the right does not change the number*

> **Goal.** len(xs ++ nil) = len(xs)
>
> $$\forall xs \in List\quad len(xs ++ nil) = len(xs)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that append empty on the right preserves length for length on List. |  |  |
| ② | We invoke the derived fact governing length on List: length adds under append, for length on List (instantiated for xs, nil). |  |  |
| ③ | We invoke the derived fact governing addition on the natural numbers: adding zero on the right does not change the number (instantiated for len(xs)). | ③ | $len(xs) + 0 = len(xs)$ |
| ④ | From step 2 and step 3, this implies len(xs plus plus nil) equals len(xs). Hence proven. | ④ | $len(xs ++ nil) = len(xs)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`List · length · append empty on the right preserves length`
