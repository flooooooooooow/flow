# examples.verify.math.derived

*Reversing a right-empty append changes nothing.*

**Source.** church — https://en.wikipedia.org/wiki/List_(abstract_data_type)

## Derived fact 1 — rev(xs ++ nil) = rev(xs)

**Coordinate.** List · reverse · reverse of append with empty is reverse · **Derived fact**

*Source: church*

*Built on: reverse distributes over append, for reverse on List, reversing empty yields empty, for reverse on List, empty is the left identity, for append on List*

> **Goal.** rev(xs ++ nil) = rev(xs)
>
> $$\forall xs \in List\quad rev(xs ++ nil) = rev(xs)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that reverse of append with empty is reverse for reverse on List. |  |  |
| ② | We invoke the derived fact governing reverse on List: reverse distributes over append, for reverse on List (instantiated for xs, nil). |  |  |
| ③ | We invoke the derived fact governing reverse on List: reversing empty yields empty, for reverse on List. |  |  |
| ④ | We invoke the definitional clause governing append on List: empty is the left identity, for append on List (instantiated for rev(xs)). |  |  |
| ⑤ | From step 2, step 3, and step 4, this implies rev(xs plus plus nil) equals rev(xs). Hence proven. | ⑤ | $rev(xs ++ nil) = rev(xs)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ⑤ | step 2, step 3, and step 4 |

`List · reverse · reverse of append with empty is reverse`
