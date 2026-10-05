# examples.verify.math.derived

*Length is a homomorphism for append.*

**Source.** church — https://en.wikipedia.org/wiki/Length_of_a_list

## Derived fact 1 — len(xs ++ ys) = len(xs) + len(ys)

**Coordinate.** List · length · length adds under append · **Derived fact**

*Source: church/induction*

*Built on: empty is the left identity, for append on List, adding zero on the right does not change the number*

> **Goal.** len(xs ++ ys) = len(xs) + len(ys)
>
> $$\forall xs \in List \forall ys \in List\quad len(xs ++ ys) = len(xs) + len(ys)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that length adds under append for length on List. |  |  |
| ② | We proceed by induction on xs: first the base case, then the inductive step. |  |  |
| ③ | Consider the base case in which xs  equals  nil. |  |  |
| ④ | We invoke the definitional clause governing append on List: empty is the left identity, for append on List (instantiated for ys). |  |  |
| ⑤ | We invoke the derived fact governing addition on the natural numbers: adding zero on the right does not change the number (instantiated for len(ys)). | ⑤ | $len(ys) + 0 = len(ys)$ |
| ⑥ | From step 3, step 4, and step 5, we can deduce that len(xs plus plus ys) equals len(xs) plus len(ys). This establishes the base case (see step 3, step 4, and step 5). Hence proven. | ⑥ | $len(xs ++ ys) = len(xs) + len(ys)$ |
| ⑦ | For the inductive step, suppose the claim holds for all smaller values. |  |  |
| ⑧ | Under the supposition in step 7, let rest = tail(xs). |  |  |
| ⑨ | Under the supposition in step 7, we cross the inductive boundary: assume the claim holds for rest (the induction hypothesis). | ⑨ | $len(rest ++ ys) = len(rest) + len(ys)$ |
| ⑩ | From step 7, step 8, and step 9, this implies len(xs plus plus ys) equals len(xs) plus len(ys). Hence proven. | ⑩ | $len(xs ++ ys) = len(xs) + len(ys)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 3 |
| ⑤ | step 3 |
| ⑥ | step 3, step 4, and step 5 |
| ⑧ | step 7 |
| ⑨ | step 7 |
| ⑩ | step 7, step 8, and step 9 |

`List · length · length adds under append`
