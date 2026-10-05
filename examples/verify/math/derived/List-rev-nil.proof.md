# examples.verify.math.derived

*Reversing the empty list yields the empty list.*

**Source.** church — https://en.wikipedia.org/wiki/List_(abstract_data_type)

## Derived fact 1 — rev(nil) = nil

**Coordinate.** List · reverse · reversing empty yields empty · **Derived fact**

*Source: church*

*Built on: empty is the left identity, for append on List, the empty list has length zero, for length on List*

> **Goal.** rev(nil) = nil
>
> $$rev(nil) = nil$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that reversing empty yields empty for reverse on List. |  |  |
| ② | We invoke the definitional clause governing append on List: empty is the left identity, for append on List (instantiated for nil). |  |  |
| ③ | We invoke the derived fact governing length on List: the empty list has length zero, for length on List. |  |  |
| ④ | From step 2 and step 3, this implies rev(nil) equals nil. Hence proven. | ④ | $rev(nil) = nil$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`List · reverse · reversing empty yields empty`
