# examples.verify.math.derived

*Zero on the left is an additive identity for naturals.*

**Source.** peano — https://en.wikipedia.org/wiki/Peano_axioms

## Derived fact 1 — 0 + n = n

**Coordinate.** the natural numbers · addition · zero on the left gives the value · **Derived fact**

*Source: peano*

*Built on: adding zero on the right does not change the number, you can swap the order when you add*

> **Goal.** 0 + n = n
>
> $$\forall n \in \mathbb{N}\quad 0 + n = n$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that zero on the left gives the value for addition on the natural numbers. |  |  |
| ② | We invoke the derived fact governing addition on the natural numbers: adding zero on the right does not change the number (instantiated for n). | ② | $n + 0 = n$ |
| ③ | We invoke the derived fact governing addition on the natural numbers: you can swap the order when you add (instantiated for 0, n). | ③ | $0 + n = n + 0$ |
| ④ | From step 2 and step 3, this implies 0 plus n equals n. Hence proven. | ④ | $0 + n = n$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`the natural numbers · addition · zero on the left gives the value`
