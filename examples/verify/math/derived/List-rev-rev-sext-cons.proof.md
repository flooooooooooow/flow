# examples.verify.math.derived

*Double reverse restores a sextuple cons list.*

**Source.** church — https://en.wikipedia.org/wiki/Reverse_(list)

## Derived fact 1 — rev(rev(cons(a, cons(b, cons(c, cons(d, cons(e, cons(f, xs))))))) = cons(a, cons(b, cons(c, cons(d, cons(e, cons(f, xs))))))

**Coordinate.** List · reverse · double reverse of sextuple cons · **Derived fact**

*Source: church*

*Built on: reverse is an involution, for reverse on List*

> **Goal.** rev(rev(cons(a, cons(b, cons(c, cons(d, cons(e, cons(f, xs))))))) = cons(a, cons(b, cons(c, cons(d, cons(e, cons(f, xs))))))
>
> $$\forall a \in \mathbb{N} \forall b \in \mathbb{N} \forall c \in \mathbb{N} \forall d \in \mathbb{N} \forall e \in \mathbb{N} \forall f \in \mathbb{N} \forall xs \in List\quad rev(rev(cons(a, cons(b, cons(c, cons(d, cons(e, cons(f, xs))))))) = cons(a, cons(b, cons(c, cons(d, cons(e, cons(f, xs))))))$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that double reverse of sextuple cons for reverse on List. |  |  |
| ② | We invoke the derived fact governing reverse on List: reverse is an involution, for reverse on List (instantiated for cons(a, cons(b, cons(c, cons(d, cons(e, cons(f, xs))))))). |  |  |
| ③ | From step 2, this implies rev(rev(cons(a, cons(b, cons(c, cons(d, cons(e, cons(f, xs))))))) equals cons(a, cons(b, cons(c, cons(d, cons(e, cons(f, xs)))))). Hence proven. | ③ | $rev(rev(cons(a, cons(b, cons(c, cons(d, cons(e, cons(f, xs))))))) = cons(a, cons(b, cons(c, cons(d, cons(e, cons(f, xs))))))$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ③ | step 2 |

`List · reverse · double reverse of sextuple cons`
