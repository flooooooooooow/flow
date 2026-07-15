# examples.verify.math.derived

*Join above meet is reflexive on equal arguments.*

**Source.** davey-priestley — *Introduction to Lattices and Order*

## Derived fact 1 — join(a, a) >= meet(a, a)

**Coordinate.** Order · lattice · join above meet reflexive · **Derived fact**

*Source: davey-priestley*

*Built on: join above meet commutes, for lattice on Order, repeating does not change the value, for join on Order*

> **Goal.** join(a, a) >= meet(a, a)
>
> $$\forall a \in \mathbb{N}\quad join(a, a) \ge meet(a, a)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that join above meet reflexive for lattice on Order. |  |  |
| ② | We invoke the derived fact governing lattice on Order: join above meet commutes, for lattice on Order (instantiated for a, a). |  |  |
| ③ | We invoke the derived fact governing join on Order: repeating does not change the value, for join on Order (instantiated for a). |  |  |
| ④ | From step 2 and step 3, this implies join(a, a) is at least meet(a, a). Hence proven. | ④ | $join(a, a) \ge meet(a, a)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`Order · lattice · join above meet reflexive`
