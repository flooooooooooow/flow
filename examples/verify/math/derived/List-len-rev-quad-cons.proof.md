# examples.verify.math.derived

*Reverse preserves length of a quadruple cons list.*

**Source.** church — https://en.wikipedia.org/wiki/Length_of_a_list

## Derived fact 1 — len(rev(cons(a, cons(b, cons(c, cons(d, nil)))))) = 4

**Coordinate.** List · length · reverse of quadruple cons has length four · **Derived fact**

*Source: church*

*Built on: reverse preserves length, for length on List, quadruple cons nil has length four, for length on List*

> **Goal.** len(rev(cons(a, cons(b, cons(c, cons(d, nil)))))) = 4
>
> $$\forall a \in \mathbb{N} \forall b \in \mathbb{N} \forall c \in \mathbb{N} \forall d \in \mathbb{N}\quad len(rev(cons(a, cons(b, cons(c, cons(d, nil)))))) = 4$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that reverse of quadruple cons has length four for length on List. |  |  |
| ② | We invoke the derived fact governing length on List: reverse preserves length, for length on List (instantiated for cons(a, cons(b, cons(c, cons(d, nil))))). |  |  |
| ③ | We invoke the derived fact governing length on List: quadruple cons nil has length four, for length on List (instantiated for a, b, c, d). |  |  |
| ④ | From step 2 and step 3, this implies len(rev(cons(a, cons(b, cons(c, cons(d, nil)))))) equals 4. Hence proven. | ④ | $len(rev(cons(a, cons(b, cons(c, cons(d, nil)))))) = 4$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`List · length · reverse of quadruple cons has length four`
