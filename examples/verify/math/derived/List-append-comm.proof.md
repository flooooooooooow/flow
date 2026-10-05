# examples.verify.math.derived

*List append commutes when lengths match trivially.*

**Source.** church — https://en.wikipedia.org/wiki/Associative_property

## Derived fact 1 — For singleton left, cons(x, nil) ++ ys = ys with head x prepended via singleton law

**Coordinate.** List · append · singleton blocks commute with append · **Derived fact**

*Source: church*

*Built on: singleton prepends the head, for append on List, parentheses do not matter, for append on List*

> **Goal.** For singleton left, cons(x, nil) ++ ys = ys with head x prepended via singleton law
>
> $$\forall x \in \mathbb{N} \forall xs \in List \forall ys \in List\quad cons(x, nil) ++ (xs ++ ys) = (cons(x, nil) ++ xs) ++ ys$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that singleton blocks commute with append for append on List. |  |  |
| ② | We invoke the definitional clause governing append on List: singleton prepends the head, for append on List (instantiated for x, xs). |  |  |
| ③ | We invoke the derived fact governing append on List: parentheses do not matter, for append on List (instantiated for cons(x, nil), xs, ys). |  |  |
| ④ | From step 2 and step 3, this implies cons(x, nil) plus plus (xs plus plus ys) equals (cons(x, nil) plus plus xs) plus plus ys. Hence proven. | ④ | $cons(x, nil) ++ (xs ++ ys) = (cons(x, nil) ++ xs) ++ ys$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`List · append · singleton blocks commute with append`
