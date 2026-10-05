# examples.verify.math.derived

*False is absorbing for conjunction on the right.*

**Source.** boole — https://en.wikipedia.org/wiki/Boolean_algebra

## Derived fact 1 — a and false = false

**Coordinate.** boolean truth values · conjunction · false is absorbing on the right · **Derived fact**

*Source: boole*

*Built on: order does not matter, for conjunction on boolean truth values, false is absorbing on the left, for conjunction on boolean truth values*

> **Goal.** a and false = false
>
> $$\forall a \in \{\mathsf{true}, \mathsf{false}\}\quad a \land \mathsf{false} = \mathsf{false}$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that false is absorbing on the right for conjunction on boolean truth values. |  |  |
| ② | We invoke the derived fact governing conjunction on boolean truth values: order does not matter, for conjunction on boolean truth values (instantiated for a, false). |  |  |
| ③ | We invoke the derived fact governing conjunction on boolean truth values: false is absorbing on the left, for conjunction on boolean truth values (instantiated for a). |  |  |
| ④ | From step 2 and step 3, this implies the conjunction of a and false equals false. Hence proven. | ④ | $a \land \mathsf{false} = \mathsf{false}$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`boolean truth values · conjunction · false is absorbing on the right`
