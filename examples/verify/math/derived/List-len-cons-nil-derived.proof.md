# examples.verify.math.derived

*Cons onto empty has length one.*

**Source.** church — https://en.wikipedia.org/wiki/Length_of_a_list

## Derived fact 1 — len(cons(x, nil)) = succ(0)

**Coordinate.** List · length · cons onto empty has length one derived · **Derived fact**

*Source: church*

*Built on: singleton has length one, for length on List*

> **Goal.** len(cons(x, nil)) = succ(0)
>
> $$\forall x \in \mathbb{N}\quad len(cons(x, nil)) = \mathrm{succ}(0)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that cons onto empty has length one derived for length on List. |  |  |
| ② | We invoke the derived fact governing length on List: singleton has length one, for length on List (instantiated for x). |  |  |
| ③ | From step 2, this implies len(cons(x, nil)) equals the successor of 0. Hence proven. | ③ | $len(cons(x, nil)) = \mathrm{succ}(0)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ③ | step 2 |

`List · length · cons onto empty has length one derived`
