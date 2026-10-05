# examples.verify.math.derived

*Appending empty on the right preserves the list.*

**Source.** church — https://en.wikipedia.org/wiki/List_(abstract_data_type)

## Derived fact 1 — xs ++ nil = xs

**Coordinate.** List · append · empty on the right gives the list · **Derived fact**

*Source: church*

*Built on: empty is the right identity, for append on List*

> **Goal.** xs ++ nil = xs
>
> $$\forall xs \in List\quad xs ++ nil = xs$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that empty on the right gives the list for append on List. |  |  |
| ② | We invoke the derived fact governing append on List: empty is the right identity, for append on List (instantiated for xs). |  |  |
| ③ | From step 2, this implies xs plus plus nil equals xs. Hence proven. | ③ | $xs ++ nil = xs$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ③ | step 2 |

`List · append · empty on the right gives the list`
