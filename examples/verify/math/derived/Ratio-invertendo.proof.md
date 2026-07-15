# examples.verify.math.derived

*Proportional magnitudes satisfy invertendo.*

**Source.** euclid — Elements, Book V, Proposition 10

## Derived fact 1 — a:b = c:d implies b:a = d:c

**Coordinate.** Ratio · proportion · invertendo holds · **Derived fact**

*Source: euclid*

*Built on: alternando holds, for proportion on Ratio, every magnitude is proportional to itself, for proportion on Ratio*

> **Goal.** a:b = c:d implies b:a = d:c
>
> $$\forall a \in Magnitude \forall b \in Magnitude \forall c \in Magnitude \forall d \in Magnitude\quad ratio(b, a) = ratio(d, c)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that invertendo holds for proportion on Ratio. |  |  |
| ② | We invoke the derived fact governing proportion on Ratio: alternando holds, for proportion on Ratio (instantiated for a, b, c, d). |  |  |
| ③ | We invoke the derived fact governing proportion on Ratio: every magnitude is proportional to itself, for proportion on Ratio (instantiated for b). |  |  |
| ④ | From step 2 and step 3, this implies ratio(b, a) equals ratio(d, c). Hence proven. | ④ | $ratio(b, a) = ratio(d, c)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`Ratio · proportion · invertendo holds`
