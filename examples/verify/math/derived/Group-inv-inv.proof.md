# examples.verify.math.derived

*The inverse of an inverse returns the original element.*

**Source.** dummit-foote — *Abstract Algebra*, §1.1

## Derived fact 1 — inv(inv(g)) = g

**Coordinate.** Group · inverse · double inverse returns the element · **Derived fact**

*Source: dummit-foote*

*Built on: left inverse recovers the identity, for inverse on Group, inverses are unique, for inverse on Group*

> **Goal.** inv(inv(g)) = g
>
> $$\forall g \in Group\quad inv(inv(g)) = g$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that double inverse returns the element for inverse on Group. |  |  |
| ② | We invoke the definitional clause governing inverse on Group: left inverse recovers the identity, for inverse on Group (instantiated for inv(g)). |  |  |
| ③ | We invoke the derived fact governing inverse on Group: inverses are unique, for inverse on Group (instantiated for g, inv(inv(g)), g). |  |  |
| ④ | From step 2 and step 3, this implies inv(inv(g)) equals g. Hence proven. | ④ | $inv(inv(g)) = g$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`Group · inverse · double inverse returns the element`
