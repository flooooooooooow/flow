# examples.verify.math.derived

*True on the right is a conjunctive identity.*

**Source.** boole — https://en.wikipedia.org/wiki/Boolean_algebra

## Derived fact 1 — a and true = a

**Coordinate.** boolean truth values · conjunction · true is the right identity from the left · **Derived fact**

*Source: boole*

*Built on: order does not matter, for conjunction on boolean truth values, true is the left identity, for conjunction on boolean truth values*

> **Goal.** a and true = a
>
> $$\forall a \in \{\mathsf{true}, \mathsf{false}\}\quad a \land \mathsf{true} = a$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that true is the right identity from the left for conjunction on boolean truth values. |  |  |
| ② | We invoke the derived fact governing conjunction on boolean truth values: order does not matter, for conjunction on boolean truth values (instantiated for a, true). |  |  |
| ③ | We invoke the derived fact governing conjunction on boolean truth values: true is the left identity, for conjunction on boolean truth values (instantiated for a). |  |  |
| ④ | From step 2 and step 3, this implies the conjunction of a and true equals a. Hence proven. | ④ | $a \land \mathsf{true} = a$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`boolean truth values · conjunction · true is the right identity from the left`
