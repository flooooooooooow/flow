# examples.verify.math.derived

*Quadruple cons ending in nil has length four.*

**Source.** church — https://en.wikipedia.org/wiki/Length_of_a_list

## Derived fact 1 — len(cons(a, cons(b, cons(c, cons(d, nil))))) = 4

**Coordinate.** List · length · quadruple cons nil has length four · **Derived fact**

*Source: church*

*Built on: cons increases length by one, for length on List, triple cons nil has length three, for length on List*

> **Goal.** len(cons(a, cons(b, cons(c, cons(d, nil))))) = 4
>
> $$\forall a \in \mathbb{N} \forall b \in \mathbb{N} \forall c \in \mathbb{N} \forall d \in \mathbb{N}\quad len(cons(a, cons(b, cons(c, cons(d, nil))))) = 4$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that quadruple cons nil has length four for length on List. |  |  |
| ② | We invoke the derived fact governing length on List: cons increases length by one, for length on List (instantiated for cons(b, cons(c, cons(d, nil)))). |  |  |
| ③ | We invoke the derived fact governing length on List: triple cons nil has length three, for length on List (instantiated for b, c, d). |  |  |
| ④ | From step 2 and step 3, this implies len(cons(a, cons(b, cons(c, cons(d, nil))))) equals 4. Hence proven. | ④ | $len(cons(a, cons(b, cons(c, cons(d, nil))))) = 4$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`List · length · quadruple cons nil has length four`
