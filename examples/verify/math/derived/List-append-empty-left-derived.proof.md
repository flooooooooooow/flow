# examples.verify.math.derived

*Empty list appended on the left changes nothing.*

**Source.** church — https://en.wikipedia.org/wiki/List_(abstract_data_type)

## Derived fact 1 — nil ++ xs = xs

**Coordinate.** List · append · empty on the left gives the list · **Derived fact**

*Source: church*

*Built on: empty is the left identity, for append on List*

> **Goal.** nil ++ xs = xs
>
> $$\forall xs \in List\quad nil ++ xs = xs$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that empty on the left gives the list for append on List. |  |  |
| ② | We invoke the definitional clause governing append on List: empty is the left identity, for append on List (instantiated for xs). |  |  |
| ③ | From step 2, this implies nil plus plus xs equals xs. Hence proven. | ③ | $nil ++ xs = xs$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ③ | step 2 |

`List · append · empty on the left gives the list`
