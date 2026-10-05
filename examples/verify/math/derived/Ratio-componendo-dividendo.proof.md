# examples.verify.math.derived

*Proportional magnitudes satisfy componendo and dividendo.*

**Source.** euclid — Elements, Book V, Proposition 13

## Derived fact 1 — a:b = c:d implies (a+b):(a-b) = (c+d):(c-d)

**Coordinate.** Ratio · proportion · componendo and dividendo hold · **Derived fact**

*Source: euclid*

*Built on: componendo holds, for proportion on Ratio, dividendo holds, for proportion on Ratio*

> **Goal.** a:b = c:d implies (a+b):(a-b) = (c+d):(c-d)
>
> $$\forall a \in Magnitude \forall b \in Magnitude \forall c \in Magnitude \forall d \in Magnitude\quad ratio(a + b, a - b) = ratio(c + d, c - d)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that componendo and dividendo hold for proportion on Ratio. |  |  |
| ② | We invoke the derived fact governing proportion on Ratio: componendo holds, for proportion on Ratio (instantiated for a, b, c, d). |  |  |
| ③ | We invoke the derived fact governing proportion on Ratio: dividendo holds, for proportion on Ratio (instantiated for a, b, c, d). |  |  |
| ④ | From step 2 and step 3, this implies ratio(a plus b, a - b) equals ratio(c plus d, c - d). Hence proven. | ④ | $ratio(a + b, a - b) = ratio(c + d, c - d)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`Ratio · proportion · componendo and dividendo hold`
