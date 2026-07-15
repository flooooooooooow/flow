# examples.verify.math.derived

*Reversing a double cons list.*

**Source.** church — https://en.wikipedia.org/wiki/Reverse_(list)

## Derived fact 1 — rev(cons(a, cons(b, nil))) = cons(b, cons(a, nil))

**Coordinate.** List · reverse · reverse of double cons · **Derived fact**

*Source: church*

*Built on: reverse of cons is append of reverse tail, for reverse on List*

> **Goal.** rev(cons(a, cons(b, nil))) = cons(b, cons(a, nil))
>
> $$\forall a \in \mathbb{N} \forall b \in \mathbb{N}\quad rev(cons(a, cons(b, nil))) = cons(b, cons(a, nil))$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that reverse of double cons for reverse on List. |  |  |
| ② | We invoke the derived fact governing reverse on List: reverse of cons is append of reverse tail, for reverse on List (instantiated for a, cons(b, nil)). |  |  |
| ③ | From step 2, this implies rev(cons(a, cons(b, nil))) equals cons(b, cons(a, nil)). Hence proven. | ③ | $rev(cons(a, cons(b, nil))) = cons(b, cons(a, nil))$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ③ | step 2 |

`List · reverse · reverse of double cons`
