# examples.verify.math.derived

*Join absorbs meet in a lattice witness.*

**Source.** davey-priestley — *Introduction to Lattices and Order*

## Derived fact 1 — join(a, meet(a, b)) = join(a, b)

**Coordinate.** Order · lattice · join absorbs meet derived · **Derived fact**

*Source: davey-priestley*

*Built on: join absorbs meet on the left, for lattice on Order, join is above the left argument, for join on Order*

> **Goal.** join(a, meet(a, b)) = join(a, b)
>
> $$\forall a \in \mathbb{N} \forall b \in \mathbb{N}\quad join(a, meet(a, b)) = join(a, b)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that join absorbs meet derived for lattice on Order. |  |  |
| ② | We invoke the derived fact governing lattice on Order: join absorbs meet on the left, for lattice on Order (instantiated for a, b). |  |  |
| ③ | We invoke the derived fact governing join on Order: join is above the left argument, for join on Order (instantiated for a, b). |  |  |
| ④ | From step 2 and step 3, this implies join(a, meet(a, b)) equals join(a, b). Hence proven. | ④ | $join(a, meet(a, b)) = join(a, b)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`Order · lattice · join absorbs meet derived`
