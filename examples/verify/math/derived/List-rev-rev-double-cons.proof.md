# examples.verify.math.derived

*Double reverse restores a double cons list.*

**Source.** church — https://en.wikipedia.org/wiki/Reverse_(list)

## Derived fact 1 — rev(rev(cons(a, cons(b, xs)))) = cons(a, cons(b, xs))

**Coordinate.** List · reverse · double reverse of double cons · **Derived fact**

*Source: church*

*Built on: reverse is an involution, for reverse on List*

> **Goal.** rev(rev(cons(a, cons(b, xs)))) = cons(a, cons(b, xs))
>
> $$\forall a \in \mathbb{N} \forall b \in \mathbb{N} \forall xs \in List\quad rev(rev(cons(a, cons(b, xs)))) = cons(a, cons(b, xs))$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that double reverse of double cons for reverse on List. |  |  |
| ② | We invoke the derived fact governing reverse on List: reverse is an involution, for reverse on List (instantiated for cons(a, cons(b, xs))). |  |  |
| ③ | From step 2, this implies rev(rev(cons(a, cons(b, xs)))) equals cons(a, cons(b, xs)). Hence proven. | ③ | $rev(rev(cons(a, cons(b, xs)))) = cons(a, cons(b, xs))$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ③ | step 2 |

`List · reverse · double reverse of double cons`
