# examples.verify.math.derived

*Reversing preserves list length.*

**Source.** church — https://en.wikipedia.org/wiki/Length_of_a_list

## Derived fact 1 — len(rev(xs)) = len(xs)

**Coordinate.** List · length · reverse preserves length · **Derived fact**

*Source: church/induction*

*Built on: reversing empty yields empty, for reverse on List, length adds under append, for length on List, reverse distributes over append, for reverse on List*

> **Goal.** len(rev(xs)) = len(xs)
>
> $$\forall xs \in List\quad len(rev(xs)) = len(xs)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that reverse preserves length for length on List. |  |  |
| ② | We proceed by induction on xs: first the base case, then the inductive step. |  |  |
| ③ | Consider the base case in which xs  equals  nil. |  |  |
| ④ | We invoke the derived fact governing reverse on List: reversing empty yields empty, for reverse on List. |  |  |
| ⑤ | We invoke the derived fact governing length on List: the empty list has length zero, for length on List. |  |  |
| ⑥ | From step 3, step 4, and step 5, we can deduce that len(rev(xs)) equals len(xs). This establishes the base case (see step 3, step 4, and step 5). Hence proven. | ⑥ | $len(rev(xs)) = len(xs)$ |
| ⑦ | For the inductive step, suppose the claim holds for all smaller values. |  |  |
| ⑧ | Under the supposition in step 7, let rest = tail(xs). |  |  |
| ⑨ | Under the supposition in step 7, we cross the inductive boundary: assume the claim holds for rest (the induction hypothesis). | ⑨ | $len(rev(rest)) = len(rest)$ |
| ⑩ | We invoke the derived fact governing reverse on List: reverse distributes over append, for reverse on List (instantiated for rest, cons(head(xs), nil)). |  |  |
| ⑪ | From step 7, step 8, step 9, and step 10, this implies len(rev(xs)) equals len(xs). Hence proven. | ⑪ | $len(rev(xs)) = len(xs)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 3 |
| ⑤ | step 3 |
| ⑥ | step 3, step 4, and step 5 |
| ⑧ | step 7 |
| ⑨ | step 7 |
| ⑪ | step 7, step 8, step 9, and step 10 |

`List · length · reverse preserves length`
