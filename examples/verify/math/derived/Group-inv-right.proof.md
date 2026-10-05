# examples.verify.math.derived

*Every group element has a right inverse.*

**Source.** dummit-foote — *Abstract Algebra*, §1.1

## Derived fact 1 — g * inv(g) = 1

**Coordinate.** Group · inverse · right inverse recovers the identity · **Derived fact**

*Source: dummit-foote*

*Built on: left inverse recovers the identity, for inverse on Group, one is the left identity, for identity on Group, parentheses do not matter, for multiplication on Group*

> **Goal.** g * inv(g) = 1
>
> $$\forall g \in Group\quad g \cdot inv(g) = 1$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that right inverse recovers the identity for inverse on Group. |  |  |
| ② | We invoke the definitional clause governing inverse on Group: left inverse recovers the identity, for inverse on Group (instantiated for g). |  |  |
| ③ | We invoke the definitional clause governing identity on Group: one is the left identity, for identity on Group (instantiated for inv(g)). |  |  |
| ④ | We invoke the definitional clause governing multiplication on Group: parentheses do not matter, for multiplication on Group (instantiated for g, inv(g), 1). |  |  |
| ⑤ | From step 2, step 3, and step 4, this implies g times inv(g) equals 1. Hence proven. | ⑤ | $g \cdot inv(g) = 1$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ⑤ | step 2, step 3, and step 4 |

`Group · inverse · right inverse recovers the identity`
