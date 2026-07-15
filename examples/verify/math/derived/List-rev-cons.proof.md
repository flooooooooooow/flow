# examples.verify.math.derived

*Reversing a cons prepends the head to the reversed tail.*

**Source.** church — https://en.wikipedia.org/wiki/List_(abstract_data_type)

## Derived fact 1 — rev(cons(x, xs)) = rev(xs) ++ cons(x, nil)

**Coordinate.** List · reverse · reverse of cons appends reversed tail · **Derived fact**

*Source: church/induction*

*Built on: reverse distributes over append, for reverse on List, singleton prepends the head, for append on List*

> **Goal.** rev(cons(x, xs)) = rev(xs) ++ cons(x, nil)
>
> $$\forall x \in \mathbb{N} \forall xs \in List\quad rev(cons(x, xs)) = rev(xs) ++ cons(x, nil)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that reverse of cons appends reversed tail for reverse on List. |  |  |
| ② | We invoke the derived fact governing reverse on List: reverse distributes over append, for reverse on List (instantiated for xs, cons(x, nil)). |  |  |
| ③ | We invoke the definitional clause governing append on List: singleton prepends the head, for append on List (instantiated for x, xs). |  |  |
| ④ | From step 2 and step 3, this implies rev(cons(x, xs)) equals rev(xs) plus plus cons(x, nil). Hence proven. | ④ | $rev(cons(x, xs)) = rev(xs) ++ cons(x, nil)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`List · reverse · reverse of cons appends reversed tail`
