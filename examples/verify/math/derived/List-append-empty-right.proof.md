# examples.verify.math.derived

*Appending the empty list on the right changes nothing.*

**Source.** church — https://en.wikipedia.org/wiki/List_(abstract_data_type)

## Derived fact 1 — xs ++ nil = xs

**Coordinate.** List · append · empty is the right identity · **Derived fact**

*Source: church/induction*

*Built on: empty is the left identity, for append on List, singleton prepends the head, for append on List*

> **Goal.** xs ++ nil = xs
>
> $$\forall xs \in List\quad xs ++ nil = xs$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that empty is the right identity for append on List. |  |  |
| ② | We proceed by induction on xs: first the base case, then the inductive step. |  |  |
| ③ | Consider the base case in which xs  equals  nil. |  |  |
| ④ | We invoke the definitional clause governing append on List: empty is the left identity, for append on List (instantiated for nil). |  |  |
| ⑤ | From step 3 and step 4, we can deduce that xs plus plus nil equals xs. This establishes the base case (see step 3 and step 4). Hence proven. | ⑤ | $xs ++ nil = xs$ |
| ⑥ | For the inductive step, suppose the claim holds for all smaller values. |  |  |
| ⑦ | Under the supposition in step 6, let x = head(xs). |  |  |
| ⑧ | Under the supposition in step 6, let rest = tail(xs). |  |  |
| ⑨ | Under the supposition in step 6, we cross the inductive boundary: assume the claim holds for rest (the induction hypothesis). | ⑨ | $rest ++ nil = rest$ |
| ⑩ | We invoke the definitional clause governing append on List: singleton prepends the head, for append on List (instantiated for x, nil). |  |  |
| ⑪ | From step 6, step 7, step 8, step 9, and step 10, this implies xs plus plus nil equals xs. Hence proven. | ⑪ | $xs ++ nil = xs$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 3 |
| ⑤ | step 3 and step 4 |
| ⑦ | step 6 |
| ⑧ | step 6 |
| ⑨ | step 6 |
| ⑪ | step 6, step 7, step 8, step 9, and step 10 |

`List · append · empty is the right identity`
