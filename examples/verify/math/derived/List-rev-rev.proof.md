# examples.verify.math.derived

*Reversing twice recovers the original list.*

**Source.** church — https://en.wikipedia.org/wiki/List_(abstract_data_type)

## Derived fact 1 — rev(rev(xs)) = xs

**Coordinate.** List · reverse · double reverse returns the list · **Derived fact**

*Source: church/induction*

*Built on: reversing empty yields empty, for reverse on List, reverse distributes over append, for reverse on List*

> **Goal.** rev(rev(xs)) = xs
>
> $$\forall xs \in List\quad rev(rev(xs)) = xs$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that double reverse returns the list for reverse on List. |  |  |
| ② | We proceed by induction on xs: first the base case, then the inductive step. |  |  |
| ③ | Consider the base case in which xs  equals  nil. |  |  |
| ④ | We invoke the derived fact governing reverse on List: reversing empty yields empty, for reverse on List. |  |  |
| ⑤ | From step 3 and step 4, we can deduce that rev(rev(xs)) equals xs. This establishes the base case (see step 3 and step 4). Hence proven. | ⑤ | $rev(rev(xs)) = xs$ |
| ⑥ | For the inductive step, suppose the claim holds for all smaller values. |  |  |
| ⑦ | Under the supposition in step 6, let rest = tail(xs). |  |  |
| ⑧ | Under the supposition in step 6, we cross the inductive boundary: assume the claim holds for rest (the induction hypothesis). | ⑧ | $rev(rev(rest)) = rest$ |
| ⑨ | We invoke the derived fact governing reverse on List: reverse distributes over append, for reverse on List (instantiated for rest, cons(head(xs), nil)). |  |  |
| ⑩ | From step 6, step 7, step 8, and step 9, this implies rev(rev(xs)) equals xs. Hence proven. | ⑩ | $rev(rev(xs)) = xs$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 3 |
| ⑤ | step 3 and step 4 |
| ⑦ | step 6 |
| ⑧ | step 6 |
| ⑩ | step 6, step 7, step 8, and step 9 |

`List · reverse · double reverse returns the list`
