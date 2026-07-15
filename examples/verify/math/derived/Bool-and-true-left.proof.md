# examples.verify.math.derived

*True on the left is a conjunctive identity.*

**Source.** boole — https://en.wikipedia.org/wiki/Boolean_algebra

## Derived fact 1 — true and a = a

**Coordinate.** boolean truth values · conjunction · true is the left identity · **Derived fact**

*Source: boole*

*Built on: order does not matter, for conjunction on boolean truth values, true is the right identity, for conjunction on boolean truth values*

> **Goal.** true and a = a
>
> $$\forall a \in \{\mathsf{true}, \mathsf{false}\}\quad \mathsf{true} \land a = a$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that true is the left identity for conjunction on boolean truth values. |  |  |
| ② | We invoke the derived fact governing conjunction on boolean truth values: order does not matter, for conjunction on boolean truth values (instantiated for true, a). |  |  |
| ③ | We invoke the derived fact governing conjunction on boolean truth values: true is the right identity, for conjunction on boolean truth values (instantiated for a). |  |  |
| ④ | From step 2 and step 3, this implies the conjunction of true and a equals a. Hence proven. | ④ | $\mathsf{true} \land a = a$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`boolean truth values · conjunction · true is the left identity`
