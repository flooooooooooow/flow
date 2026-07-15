# examples.verify.math.derived

*Appending two empty lists yields empty.*

**Source.** church — https://en.wikipedia.org/wiki/List_(abstract_data_type)

## Derived fact 1 — nil ++ nil = nil

**Coordinate.** List · append · empty append empty is empty · **Derived fact**

*Source: church*

*Built on: empty is the left identity, for append on List, the empty list has length zero, for length on List*

> **Goal.** nil ++ nil = nil
>
> $$nil ++ nil = nil$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that empty append empty is empty for append on List. |  |  |
| ② | We invoke the definitional clause governing append on List: empty is the left identity, for append on List (instantiated for nil). |  |  |
| ③ | We invoke the derived fact governing length on List: the empty list has length zero, for length on List. |  |  |
| ④ | From step 2 and step 3, this implies nil plus plus nil equals nil. Hence proven. | ④ | $nil ++ nil = nil$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`List · append · empty append empty is empty`
