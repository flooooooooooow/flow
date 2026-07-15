# examples.verify.math.derived

*Join of join and meet is idempotent on the left.*

**Source.** davey-priestley — *Introduction to Lattices and Order*

## Derived fact 1 — join(join(a, b), meet(a, b)) = join(a, b)

**Coordinate.** Order · lattice · join idempotent with meet · **Derived fact**

*Source: davey-priestley*

*Built on: join absorbs meet derived, for lattice on Order, repeating does not change the value, for join on Order*

> **Goal.** join(join(a, b), meet(a, b)) = join(a, b)
>
> $$\forall a \in \mathbb{N} \forall b \in \mathbb{N}\quad join(join(a, b), meet(a, b)) = join(a, b)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that join idempotent with meet for lattice on Order. |  |  |
| ② | We invoke the derived fact governing lattice on Order: join absorbs meet derived, for lattice on Order (instantiated for a, b). |  |  |
| ③ | We invoke the derived fact governing join on Order: repeating does not change the value, for join on Order (instantiated for join(a, b)). |  |  |
| ④ | From step 2 and step 3, this implies join(join(a, b), meet(a, b)) equals join(a, b). Hence proven. | ④ | $join(join(a, b), meet(a, b)) = join(a, b)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`Order · lattice · join idempotent with meet`
