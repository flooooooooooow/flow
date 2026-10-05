# examples.verify.math.derived

*Sextuple cons ending in nil has length six.*

**Source.** church — https://en.wikipedia.org/wiki/Length_of_a_list

## Derived fact 1 — len(cons(a, cons(b, cons(c, cons(d, cons(e, cons(f, nil))))))) = 6

**Coordinate.** List · length · sextuple cons nil has length six · **Derived fact**

*Source: church*

*Built on: cons increases length by one, for length on List, quintuple cons nil has length five, for length on List*

> **Goal.** len(cons(a, cons(b, cons(c, cons(d, cons(e, cons(f, nil))))))) = 6
>
> $$\forall a \in \mathbb{N} \forall b \in \mathbb{N} \forall c \in \mathbb{N} \forall d \in \mathbb{N} \forall e \in \mathbb{N} \forall f \in \mathbb{N}\quad len(cons(a, cons(b, cons(c, cons(d, cons(e, cons(f, nil))))))) = 6$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that sextuple cons nil has length six for length on List. |  |  |
| ② | We invoke the derived fact governing length on List: cons increases length by one, for length on List (instantiated for cons(b, cons(c, cons(d, cons(e, cons(f, nil)))))). |  |  |
| ③ | We invoke the derived fact governing length on List: quintuple cons nil has length five, for length on List (instantiated for b, c, d, e, f). |  |  |
| ④ | From step 2 and step 3, this implies len(cons(a, cons(b, cons(c, cons(d, cons(e, cons(f, nil))))))) equals 6. Hence proven. | ④ | $len(cons(a, cons(b, cons(c, cons(d, cons(e, cons(f, nil))))))) = 6$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`List · length · sextuple cons nil has length six`
