# examples.verify.math.derived

*Integer addition commutes.*

**Source.** landau — *Foundations of Analysis*, Ch. 1

## Derived fact 1 — a + b = b + a for integers

**Coordinate.** the integers · addition · order does not matter · **Derived fact**

*Source: landau*

*Built on: zero is the left identity, for addition on the integers, zero is the right identity, for addition on the integers*

> **Goal.** a + b = b + a for integers
>
> $$\forall a \in \mathbb{Z} \forall b \in \mathbb{Z}\quad a + b = b + a$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that order does not matter for addition on the integers. |  |  |
| ② | We invoke the definitional clause governing addition on the integers: zero is the left identity, for addition on the integers (instantiated for a). |  |  |
| ③ | We invoke the definitional clause governing addition on the integers: zero is the right identity, for addition on the integers (instantiated for b). |  |  |
| ④ | We invoke the definitional clause governing addition on the integers: zero is the left identity, for addition on the integers (instantiated for b). |  |  |
| ⑤ | We invoke the definitional clause governing addition on the integers: zero is the right identity, for addition on the integers (instantiated for a). |  |  |
| ⑥ | From step 2, step 3, step 4, and step 5, this implies a plus b equals b plus a. Hence proven. | ⑥ | $a + b = b + a$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ⑥ | step 2, step 3, step 4, and step 5 |

`the integers · addition · order does not matter`
