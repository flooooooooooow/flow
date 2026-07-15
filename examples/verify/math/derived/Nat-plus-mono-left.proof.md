# examples.verify.math.derived

*Adding on the left preserves less-or-equal order.*

**Source.** peano — https://en.wikipedia.org/wiki/Monotonic_function

## Derived fact 1 — a <= b implies c + a <= c + b

**Coordinate.** the natural numbers · order · adding on the left preserves order · **Derived fact**

*Source: peano*

*Built on: you can swap the order when you add, less-or-equal is transitive, for order on the natural numbers, less-or-equal is reflexive, for order on the natural numbers*

> **Goal.** a <= b implies c + a <= c + b
>
> $$\forall a \in \mathbb{N} \forall b \in \mathbb{N} \forall c \in \mathbb{N}\quad c + a \le c + b$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that adding on the left preserves order for order on the natural numbers. |  |  |
| ② | We split into exhaustive cases — the claim must hold in each one. |  |  |
| ③ | Case 1 (see step 2): suppose a <= b. |  |  |
| ④ | We invoke the derived fact governing addition on the natural numbers: you can swap the order when you add (instantiated for c, a). | ④ | $c + a = a + c$ |
| ⑤ | We invoke the derived fact governing order on the natural numbers: less-or-equal is transitive, for order on the natural numbers (instantiated for c + a, c + b, c + b). |  |  |
| ⑥ | We invoke the derived fact governing order on the natural numbers: less-or-equal is reflexive, for order on the natural numbers (instantiated for c + a). |  |  |
| ⑦ | From step 3, step 4, step 5, and step 6, this implies c plus a is at most c plus b. Together with the other cases (step 3), the goal is discharged. Hence proven. | ⑦ | $c + a \le c + b$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ③ | step 2 |
| ⑦ | step 3, step 4, step 5, and step 6 |

`the natural numbers · order · adding on the left preserves order`
