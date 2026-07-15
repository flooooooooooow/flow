# examples.verify.math.derived

*Reverse preserves length of a quintuple cons list.*

**Source.** church — https://en.wikipedia.org/wiki/Length_of_a_list

## Derived fact 1 — len(rev(cons(a, cons(b, cons(c, cons(d, cons(e, nil))))))) = 5

**Coordinate.** List · length · reverse of quintuple cons has length five · **Derived fact**

*Source: church*

*Built on: reverse preserves length, for length on List, quintuple cons nil has length five, for length on List*

> **Goal.** len(rev(cons(a, cons(b, cons(c, cons(d, cons(e, nil))))))) = 5
>
> $$\forall a \in \mathbb{N} \forall b \in \mathbb{N} \forall c \in \mathbb{N} \forall d \in \mathbb{N} \forall e \in \mathbb{N}\quad len(rev(cons(a, cons(b, cons(c, cons(d, cons(e, nil))))))) = 5$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that reverse of quintuple cons has length five for length on List. |  |  |
| ② | We invoke the derived fact governing length on List: reverse preserves length, for length on List (instantiated for cons(a, cons(b, cons(c, cons(d, cons(e, nil)))))). |  |  |
| ③ | We invoke the derived fact governing length on List: quintuple cons nil has length five, for length on List (instantiated for a, b, c, d, e). |  |  |
| ④ | From step 2 and step 3, this implies len(rev(cons(a, cons(b, cons(c, cons(d, cons(e, nil))))))) equals 5. Hence proven. | ④ | $len(rev(cons(a, cons(b, cons(c, cons(d, cons(e, nil))))))) = 5$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`List · length · reverse of quintuple cons has length five`
