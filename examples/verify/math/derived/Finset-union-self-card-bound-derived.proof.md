# examples.verify.math.derived

*Union with self does not increase cardinality.*

**Source.** Finset union self card bound

## Derived fact 1 — Union with self does not increase cardinality

**Coordinate.** Finset · union · self card bound derived · **Derived fact**

*Source: Finset union self card bound*

*Built on: self card bound derived, for union on Finset*

> **Goal.** Union with self does not increase cardinality
>
> $$\forall s \in \guillemotleft{}Finset\guillemotright{} \guillemotleft{}Nat\guillemotright{}\quad «Finset» «card»(«Finset» «union»(s, s)) \le «Finset» «card»(s)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that self card bound derived for union on Finset. |  |  |
| ② | We invoke the derived fact: «Finset» «card» (instantiated for «Finset» «union»(s, s)) <= «Finset» «card»(s). |  |  |
| ③ | From step 2, this implies «Finset» «card»(«Finset» «union»(s, s)) is at most «Finset» «card»(s). Hence proven. | ③ | $«Finset» «card»(«Finset» «union»(s, s)) \le «Finset» «card»(s)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ③ | step 2 |

`Finset · union · self card bound derived`
