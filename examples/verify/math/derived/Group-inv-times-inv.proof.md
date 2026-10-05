# examples.verify.math.derived

*Inverse times inverse gives identity in a group.*

**Source.** dummit-foote — *Abstract Algebra*, §1.1

## Derived fact 1 — inv(a) * inv(a) = 1 when a * inv(a) = 1

**Coordinate.** Group · inverse · inverse times inverse is identity · **Derived fact**

*Source: dummit-foote*

*Built on: right inverse cancels on the right, for inverse on Group, inverse of inverse is original, for inverse on Group*

> **Goal.** inv(a) * inv(a) = 1 when a * inv(a) = 1
>
> $$\forall a \in Group\quad inv(a) * inv(a) = 1$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that inverse times inverse is identity for inverse on Group. |  |  |
| ② | We invoke the derived fact governing inverse on Group: right inverse cancels on the right, for inverse on Group (instantiated for a, inv(a)). |  |  |
| ③ | We invoke the derived fact governing inverse on Group: inverse of inverse is original, for inverse on Group (instantiated for a). |  |  |
| ④ | From step 2 and step 3, this implies inv(a) times inv(a) equals 1. Hence proven. | ④ | $inv(a) * inv(a) = 1$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`Group · inverse · inverse times inverse is identity`
