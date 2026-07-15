# examples.verify.math.derived

*Nonuple cons ending in nil has length nine.*

**Source.** church — https://en.wikipedia.org/wiki/Length_of_a_list

## Derived fact 1 — len of nine cons ending in nil equals 9

**Coordinate.** List · length · nonuple cons nil has length nine · **Derived fact**

*Source: church*

*Built on: cons increases length by one, for length on List, octuple cons nil has length eight, for length on List*

> **Goal.** len of nine cons ending in nil equals 9
>
> $$\forall a \in \mathbb{N} \forall b \in \mathbb{N} \forall c \in \mathbb{N} \forall d \in \mathbb{N} \forall e \in \mathbb{N} \forall f \in \mathbb{N} \forall g \in \mathbb{N} \forall h \in \mathbb{N} \forall i \in \mathbb{N}\quad len(cons(a, cons(b, cons(c, cons(d, cons(e, cons(f, cons(g, cons(h, cons(i, nil)))))))))) = 9$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that nonuple cons nil has length nine for length on List. |  |  |
| ② | We invoke the derived fact governing length on List: cons increases length by one, for length on List (instantiated for cons(b, cons(c, cons(d, cons(e, cons(f, cons(g, cons(h, cons(i, nil))))))))). |  |  |
| ③ | We invoke the derived fact governing length on List: octuple cons nil has length eight, for length on List (instantiated for b, c, d, e, f, g, h, i). |  |  |
| ④ | From step 2 and step 3, this implies len(cons(a, cons(b, cons(c, cons(d, cons(e, cons(f, cons(g, cons(h, cons(i, nil)))))))))) equals 9. Hence proven. | ④ | $len(cons(a, cons(b, cons(c, cons(d, cons(e, cons(f, cons(g, cons(h, cons(i, nil)))))))))) = 9$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`List · length · nonuple cons nil has length nine`
