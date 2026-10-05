# examples.verify.math.derived

*Reverse distributes over append.*

**Source.** church — https://en.wikipedia.org/wiki/List_(abstract_data_type)

## Derived fact 1 — rev(xs ++ ys) = rev(ys) ++ rev(xs)

**Coordinate.** List · reverse · reverse distributes over append · **Derived fact**

*Source: church/induction*

*Built on: empty is the left identity, for append on List, reversing empty yields empty, for reverse on List, parentheses do not matter, for append on List*

> **Goal.** rev(xs ++ ys) = rev(ys) ++ rev(xs)
>
> $$\forall xs \in List \forall ys \in List\quad rev(xs ++ ys) = rev(ys) ++ rev(xs)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that reverse distributes over append for reverse on List. |  |  |
| ② | We proceed by induction on xs: first the base case, then the inductive step. |  |  |
| ③ | Consider the base case in which xs  equals  nil. |  |  |
| ④ | We invoke the derived fact governing reverse on List: reversing empty yields empty, for reverse on List. |  |  |
| ⑤ | We invoke the definitional clause governing append on List: empty is the left identity, for append on List (instantiated for ys). |  |  |
| ⑥ | From step 3, step 4, and step 5, we can deduce that rev(xs plus plus ys) equals rev(ys) plus plus rev(xs). This establishes the base case (see step 3, step 4, and step 5). Hence proven. | ⑥ | $rev(xs ++ ys) = rev(ys) ++ rev(xs)$ |
| ⑦ | For the inductive step, suppose the claim holds for all smaller values. |  |  |
| ⑧ | Under the supposition in step 7, let rest = tail(xs). |  |  |
| ⑨ | Under the supposition in step 7, we cross the inductive boundary: assume the claim holds for rest (the induction hypothesis). | ⑨ | $rev(rest ++ ys) = rev(ys) ++ rev(rest)$ |
| ⑩ | We invoke the derived fact governing append on List: parentheses do not matter, for append on List (instantiated for rest, ys, rev(xs)). |  |  |
| ⑪ | From step 7, step 8, step 9, and step 10, this implies rev(xs plus plus ys) equals rev(ys) plus plus rev(xs). Hence proven. | ⑪ | $rev(xs ++ ys) = rev(ys) ++ rev(xs)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 3 |
| ⑤ | step 3 |
| ⑥ | step 3, step 4, and step 5 |
| ⑧ | step 7 |
| ⑨ | step 7 |
| ⑪ | step 7, step 8, step 9, and step 10 |

`List · reverse · reverse distributes over append`
