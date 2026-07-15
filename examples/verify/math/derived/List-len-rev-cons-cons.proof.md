# examples.verify.math.derived

*Reversing a two-element list preserves length two.*

**Source.** church — https://en.wikipedia.org/wiki/Length_of_a_list

## Derived fact 1 — len(rev(cons(x, cons(y, nil)))) = succ(succ(0))

**Coordinate.** List · length · reverse of pair list has length two · **Derived fact**

*Source: church*

*Built on: reverse preserves length, for length on List, pair list has length two, for length on List*

> **Goal.** len(rev(cons(x, cons(y, nil)))) = succ(succ(0))
>
> $$\forall x \in \mathbb{N} \forall y \in \mathbb{N}\quad len(rev(cons(x, cons(y, nil)))) = \mathrm{succ}(succ(0))$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that reverse of pair list has length two for length on List. |  |  |
| ② | We invoke the derived fact governing length on List: reverse preserves length, for length on List (instantiated for cons(x, cons(y, nil))). |  |  |
| ③ | We invoke the derived fact governing length on List: pair list has length two, for length on List (instantiated for x, y). |  |  |
| ④ | From step 2 and step 3, this implies len(rev(cons(x, cons(y, nil)))) equals the successor of succ(0). Hence proven. | ④ | $len(rev(cons(x, cons(y, nil)))) = \mathrm{succ}(succ(0))$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`List · length · reverse of pair list has length two`
