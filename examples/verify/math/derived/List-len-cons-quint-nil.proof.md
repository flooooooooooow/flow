# examples.verify.math.derived

*Quintuple cons ending in nil has length five.*

**Source.** church — https://en.wikipedia.org/wiki/Length_of_a_list

## Derived fact 1 — len(cons(a, cons(b, cons(c, cons(d, cons(e, nil)))))) = 5

**Coordinate.** List · length · quintuple cons nil has length five · **Derived fact**

*Source: church*

*Built on: cons increases length by one, for length on List, quadruple cons nil has length four, for length on List*

> **Goal.** len(cons(a, cons(b, cons(c, cons(d, cons(e, nil)))))) = 5
>
> $$\forall a \in \mathbb{N} \forall b \in \mathbb{N} \forall c \in \mathbb{N} \forall d \in \mathbb{N} \forall e \in \mathbb{N}\quad len(cons(a, cons(b, cons(c, cons(d, cons(e, nil)))))) = 5$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that quintuple cons nil has length five for length on List. |  |  |
| ② | We invoke the derived fact governing length on List: cons increases length by one, for length on List (instantiated for cons(b, cons(c, cons(d, cons(e, nil))))). |  |  |
| ③ | We invoke the derived fact governing length on List: quadruple cons nil has length four, for length on List (instantiated for b, c, d, e). |  |  |
| ④ | From step 2 and step 3, this implies len(cons(a, cons(b, cons(c, cons(d, cons(e, nil)))))) equals 5. Hence proven. | ④ | $len(cons(a, cons(b, cons(c, cons(d, cons(e, nil)))))) = 5$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`List · length · quintuple cons nil has length five`
