# examples.verify.math.derived

*Proportional magnitudes satisfy componendo.*

**Source.** euclid — Elements, Book V, Proposition 11

## Derived fact 1 — a:b = c:d implies (a+b):b = (c+d):d

**Coordinate.** Ratio · proportion · componendo holds · **Derived fact**

*Source: euclid*

*Built on: alternando holds, for proportion on Ratio, invertendo holds, for proportion on Ratio*

> **Goal.** a:b = c:d implies (a+b):b = (c+d):d
>
> $$\forall a \in Magnitude \forall b \in Magnitude \forall c \in Magnitude \forall d \in Magnitude\quad ratio(a + b, b) = ratio(c + d, d)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that componendo holds for proportion on Ratio. |  |  |
| ② | We invoke the derived fact governing proportion on Ratio: alternando holds, for proportion on Ratio (instantiated for a, b, c, d). |  |  |
| ③ | We invoke the derived fact governing proportion on Ratio: invertendo holds, for proportion on Ratio (instantiated for a, b, c, d). |  |  |
| ④ | From step 2 and step 3, this implies ratio(a plus b, b) equals ratio(c plus d, d). Hence proven. | ④ | $ratio(a + b, b) = ratio(c + d, d)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`Ratio · proportion · componendo holds`
