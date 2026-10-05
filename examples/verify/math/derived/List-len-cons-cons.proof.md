# examples.verify.math.derived

*A two-element list has length two.*

**Source.** church — https://en.wikipedia.org/wiki/Length_of_a_list

## Derived fact 1 — len(cons(x, cons(y, nil))) = succ(succ(0))

**Coordinate.** List · length · pair list has length two · **Derived fact**

*Source: church*

*Built on: cons increases length by one, for length on List, singleton has length one, for length on List*

> **Goal.** len(cons(x, cons(y, nil))) = succ(succ(0))
>
> $$\forall x \in \mathbb{N} \forall y \in \mathbb{N}\quad len(cons(x, cons(y, nil))) = \mathrm{succ}(succ(0))$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that pair list has length two for length on List. |  |  |
| ② | We invoke the derived fact governing length on List: cons increases length by one, for length on List (instantiated for x, cons(y, nil)). |  |  |
| ③ | We invoke the derived fact governing length on List: singleton has length one, for length on List (instantiated for y). |  |  |
| ④ | From step 2 and step 3, this implies len(cons(x, cons(y, nil))) equals the successor of succ(0). Hence proven. | ④ | $len(cons(x, cons(y, nil))) = \mathrm{succ}(succ(0))$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`List · length · pair list has length two`
