# examples.verify.math.derived

*Appending a singleton increases length by one.*

**Source.** church — https://en.wikipedia.org/wiki/Length_of_a_list

## Derived fact 1 — len(xs ++ cons(y, nil)) = succ(len(xs))

**Coordinate.** List · length · append singleton increases length by one · **Derived fact**

*Source: church*

*Built on: length adds under append, for length on List, successor on the right via commutativity, for addition on the natural numbers*

> **Goal.** len(xs ++ cons(y, nil)) = succ(len(xs))
>
> $$\forall xs \in List \forall y \in \mathbb{N}\quad len(xs ++ cons(y, nil)) = \mathrm{succ}(len(xs))$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that append singleton increases length by one for length on List. |  |  |
| ② | We invoke the derived fact governing length on List: length adds under append, for length on List (instantiated for xs, cons(y, nil)). |  |  |
| ③ | We invoke the derived fact governing addition on the natural numbers: successor on the right via commutativity, for addition on the natural numbers (instantiated for len(xs), 0). |  |  |
| ④ | From step 2 and step 3, this implies len(xs plus plus cons(y, nil)) equals the successor of len(xs). Hence proven. | ④ | $len(xs ++ cons(y, nil)) = \mathrm{succ}(len(xs))$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`List · length · append singleton increases length by one`
