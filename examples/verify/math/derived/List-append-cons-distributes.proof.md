# examples.verify.math.derived

*Cons distributes over list append.*

**Source.** church — https://en.wikipedia.org/wiki/List_(abstract_data_type)

## Derived fact 1 — cons(x, xs) ++ ys = cons(x, xs ++ ys)

**Coordinate.** List · append · cons distributes over append · **Derived fact**

*Source: church*

*Built on: singleton prepends the head, for append on List, parentheses do not matter, for append on List*

> **Goal.** cons(x, xs) ++ ys = cons(x, xs ++ ys)
>
> $$\forall x \in \mathbb{N} \forall xs \in List \forall ys \in List\quad cons(x, xs) ++ ys = cons(x, xs ++ ys)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that cons distributes over append for append on List. |  |  |
| ② | We invoke the definitional clause governing append on List: singleton prepends the head, for append on List (instantiated for x, xs). |  |  |
| ③ | We invoke the derived fact governing append on List: parentheses do not matter, for append on List (instantiated for cons(x, nil), xs, ys). |  |  |
| ④ | From step 2 and step 3, this implies cons(x, xs) plus plus ys equals cons(x, xs plus plus ys). Hence proven. | ④ | $cons(x, xs) ++ ys = cons(x, xs ++ ys)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`List · append · cons distributes over append`
