# examples.verify.math.derived

*The inverse of a product reverses the factors.*

**Source.** dummit-foote — *Abstract Algebra*, §1.1

## Derived fact 1 — inv(a * b) = inv(b) * inv(a)

**Coordinate.** Group · inverse · product inverses reverse order · **Derived fact**

*Source: dummit-foote*

*Built on: right inverse recovers the identity, for inverse on Group, inverses are unique, for inverse on Group, parentheses do not matter, for multiplication on Group*

> **Goal.** inv(a * b) = inv(b) * inv(a)
>
> $$\forall a \in Group \forall b \in Group\quad inv(a \cdot b) = inv(b) * inv(a)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that product inverses reverse order for inverse on Group. |  |  |
| ② | We invoke the derived fact governing inverse on Group: right inverse recovers the identity, for inverse on Group (instantiated for a). |  |  |
| ③ | We invoke the derived fact governing inverse on Group: right inverse recovers the identity, for inverse on Group (instantiated for b). |  |  |
| ④ | We invoke the derived fact governing inverse on Group: inverses are unique, for inverse on Group (instantiated for a * b, inv(b) * inv(a), inv(a * b)). |  |  |
| ⑤ | We invoke the definitional clause governing multiplication on Group: parentheses do not matter, for multiplication on Group (instantiated for a, b, inv(b)). |  |  |
| ⑥ | From step 2, step 3, step 4, and step 5, this implies inv(a times b) equals inv(b) times inv(a). Hence proven. | ⑥ | $inv(a \cdot b) = inv(b) * inv(a)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ⑥ | step 2, step 3, step 4, and step 5 |

`Group · inverse · product inverses reverse order`
