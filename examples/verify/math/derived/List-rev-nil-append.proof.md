# examples.verify.math.derived

*Reversing an empty left append changes nothing.*

**Source.** church — https://en.wikipedia.org/wiki/List_(abstract_data_type)

## Derived fact 1 — rev(nil ++ xs) = rev(xs)

**Coordinate.** List · reverse · reverse of empty append is reverse · **Derived fact**

*Source: church*

*Built on: empty is the left identity, for append on List, reversing empty yields empty, for reverse on List*

> **Goal.** rev(nil ++ xs) = rev(xs)
>
> $$\forall xs \in List\quad rev(nil ++ xs) = rev(xs)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that reverse of empty append is reverse for reverse on List. |  |  |
| ② | We invoke the definitional clause governing append on List: empty is the left identity, for append on List (instantiated for xs). |  |  |
| ③ | We invoke the derived fact governing reverse on List: reversing empty yields empty, for reverse on List. |  |  |
| ④ | From step 2 and step 3, this implies rev(nil plus plus xs) equals rev(xs). Hence proven. | ④ | $rev(nil ++ xs) = rev(xs)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`List · reverse · reverse of empty append is reverse`
