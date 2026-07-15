# examples.verify.math.derived

*Length increases by one under cons.*

**Source.** church — https://en.wikipedia.org/wiki/Length_of_a_list

## Derived fact 1 — len(cons(x, xs)) = succ(len(xs))

**Coordinate.** List · length · cons increases length by one · **Derived fact**

*Source: church/induction*

*Built on: length adds under append, for length on List, singleton prepends the head, for append on List*

> **Goal.** len(cons(x, xs)) = succ(len(xs))
>
> $$\forall x \in \mathbb{N} \forall xs \in List\quad len(cons(x, xs)) = \mathrm{succ}(len(xs))$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that cons increases length by one for length on List. |  |  |
| ② | We invoke the derived fact governing length on List: length adds under append, for length on List (instantiated for cons(x, nil), xs). |  |  |
| ③ | We invoke the definitional clause governing append on List: singleton prepends the head, for append on List (instantiated for x, xs). |  |  |
| ④ | From step 2 and step 3, this implies len(cons(x, xs)) equals the successor of len(xs). Hence proven. | ④ | $len(cons(x, xs)) = \mathrm{succ}(len(xs))$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`List · length · cons increases length by one`
