# examples.verify.math.derived

*Rational addition commutes.*

**Source.** landau — *Foundations of Analysis*

## Derived fact 1 — p + q = q + p for rationals

**Coordinate.** Rat · addition · order does not matter · **Derived fact**

*Source: landau*

*Built on: zero is the left identity, for addition on Rat, zero is the right identity, for addition on Rat*

> **Goal.** p + q = q + p for rationals
>
> $$\forall p \in Rat \forall q \in Rat\quad p + q = q + p$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that order does not matter for addition on Rat. |  |  |
| ② | We invoke the definitional clause governing addition on Rat: zero is the left identity, for addition on Rat (instantiated for p). |  |  |
| ③ | We invoke the definitional clause governing addition on Rat: zero is the right identity, for addition on Rat (instantiated for q). |  |  |
| ④ | We invoke the definitional clause governing addition on Rat: zero is the left identity, for addition on Rat (instantiated for q). |  |  |
| ⑤ | We invoke the definitional clause governing addition on Rat: zero is the right identity, for addition on Rat (instantiated for p). |  |  |
| ⑥ | From step 2, step 3, step 4, and step 5, this implies p plus q equals q plus p. Hence proven. | ⑥ | $p + q = q + p$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ⑥ | step 2, step 3, step 4, and step 5 |

`Rat · addition · order does not matter`
