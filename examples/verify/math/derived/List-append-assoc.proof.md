# examples.verify.math.derived

*List append associates.*

**Source.** church — https://en.wikipedia.org/wiki/Associative_property

## Derived fact 1 — (xs ++ ys) ++ zs = xs ++ (ys ++ zs)

**Coordinate.** List · append · parentheses do not matter · **Derived fact**

*Source: church/induction — standard list induction*

*Built on: empty is the left identity, for append on List, singleton prepends the head, for append on List*

> **Goal.** (xs ++ ys) ++ zs = xs ++ (ys ++ zs)
>
> $$\forall xs \in List \forall ys \in List \forall zs \in List\quad (xs ++ ys) ++ zs = xs ++ (ys ++ zs)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that parentheses do not matter for append on List. |  |  |
| ② | We proceed by induction on xs: first the base case, then the inductive step. |  |  |
| ③ | Consider the base case in which xs  equals  nil. |  |  |
| ④ | We invoke the definitional clause governing append on List: empty is the left identity, for append on List (instantiated for ys). |  |  |
| ⑤ | We invoke the definitional clause governing append on List: empty is the left identity, for append on List (instantiated for cons(0, zs)). |  |  |
| ⑥ | From step 3, step 4, and step 5, we can deduce that (xs plus plus ys) plus plus zs equals xs plus plus (ys plus plus zs). This establishes the base case (see step 3, step 4, and step 5). Hence proven. | ⑥ | $(xs ++ ys) ++ zs = xs ++ (ys ++ zs)$ |
| ⑦ | For the inductive step, suppose the claim holds for all smaller values. |  |  |
| ⑧ | Under the supposition in step 7, let x = head(xs). |  |  |
| ⑨ | Under the supposition in step 7, let rest = tail(xs). |  |  |
| ⑩ | Under the supposition in step 7, we cross the inductive boundary: assume the claim holds for rest (the induction hypothesis). | ⑩ | $(rest ++ ys) ++ zs = rest ++ (ys ++ zs)$ |
| ⑪ | We invoke the definitional clause governing append on List: singleton prepends the head, for append on List (instantiated for x, ys). |  |  |
| ⑫ | From step 7, step 8, step 9, step 10, and step 11, this implies (xs plus plus ys) plus plus zs equals xs plus plus (ys plus plus zs). Hence proven. | ⑫ | $(xs ++ ys) ++ zs = xs ++ (ys ++ zs)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 3 |
| ⑤ | step 3 |
| ⑥ | step 3, step 4, and step 5 |
| ⑧ | step 7 |
| ⑨ | step 7 |
| ⑩ | step 7 |
| ⑫ | step 7, step 8, step 9, step 10, and step 11 |

`List · append · parentheses do not matter`
