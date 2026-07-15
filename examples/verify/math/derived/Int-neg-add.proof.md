# examples.verify.math.derived

*Negation distributes over integer addition.*

**Source.** landau — *Foundations of Analysis*, Ch. 1

## Derived fact 1 — -(a + b) = (-a) + (-b)

**Coordinate.** the integers · negation · negation distributes over addition · **Derived fact**

*Source: landau*

*Built on: double negation returns the value, for negation on the integers, zero is the right identity, for addition on the integers*

> **Goal.** -(a + b) = (-a) + (-b)
>
> $$\forall a \in \mathbb{Z} \forall b \in \mathbb{Z}\quad -(a + b) = (-a) + (-b)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that negation distributes over addition for negation on the integers. |  |  |
| ② | We invoke the derived fact governing negation on the integers: double negation returns the value, for negation on the integers (instantiated for a). |  |  |
| ③ | We invoke the derived fact governing negation on the integers: double negation returns the value, for negation on the integers (instantiated for b). |  |  |
| ④ | We invoke the definitional clause governing addition on the integers: zero is the right identity, for addition on the integers (instantiated for a + b). |  |  |
| ⑤ | From step 2, step 3, and step 4, this implies -(a plus b) equals (-a) plus (-b). Hence proven. | ⑤ | $-(a + b) = (-a) + (-b)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ⑤ | step 2, step 3, and step 4 |

`the integers · negation · negation distributes over addition`
