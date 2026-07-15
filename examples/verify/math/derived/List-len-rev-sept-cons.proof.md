# examples.verify.math.derived

*Reverse preserves length of a septuple cons list.*

**Source.** church — https://en.wikipedia.org/wiki/Length_of_a_list

## Derived fact 1 — len(rev(septuple cons ending in nil)) = 7

**Coordinate.** List · length · reverse of septuple cons has length seven · **Derived fact**

*Source: church*

*Built on: reverse preserves length, for length on List, septuple cons nil has length seven, for length on List*

> **Goal.** len(rev(septuple cons ending in nil)) = 7
>
> $$\forall a \in \mathbb{N} \forall b \in \mathbb{N} \forall c \in \mathbb{N} \forall d \in \mathbb{N} \forall e \in \mathbb{N} \forall f \in \mathbb{N} \forall g \in \mathbb{N}\quad len(rev(cons(a, cons(b, cons(c, cons(d, cons(e, cons(f, cons(g, nil)))))))) = 7$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that reverse of septuple cons has length seven for length on List. |  |  |
| ② | We invoke the derived fact governing length on List: reverse preserves length, for length on List (instantiated for cons(a, cons(b, cons(c, cons(d, cons(e, cons(f, cons(g, nil)))))))). |  |  |
| ③ | We invoke the derived fact governing length on List: septuple cons nil has length seven, for length on List (instantiated for a, b, c, d, e, f, g). |  |  |
| ④ | From step 2 and step 3, this implies len(rev(cons(a, cons(b, cons(c, cons(d, cons(e, cons(f, cons(g, nil)))))))) equals 7. Hence proven. | ④ | $len(rev(cons(a, cons(b, cons(c, cons(d, cons(e, cons(f, cons(g, nil)))))))) = 7$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`List · length · reverse of septuple cons has length seven`
