# full_adder

*The full adder output matches binary addition with carry.*

**Source.** patterson: Patterson & Hennessy, *Computer Organization and Design*, §A.5

## Derived fact 1: Correct

**Coordinate.** FullAdder · output · output matches specification · **Derived fact**

> **Goal.** We're showing that result.Sum equals expected.the conjunction of sum and result.Cout equals expected.carry.
>
> $$\forall A \in \mathbb{Z} \forall B \in \mathbb{Z} \forall Cin \in \mathbb{Z}\quad result.Sum = expected.sum \land result.Cout = expected.carry$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | Let result = FullAdder(A, B, Cin). |  |  |
| ② | Let expected = binary_add_1bit(A, B, Cin). |  |  |
| ③ | From step 1 and step 2, this implies result.Sum equals expected.the conjunction of sum and result.Cout equals expected.carry. Hence proven. | ③ | $result.Sum = expected.sum \land result.Cout = expected.carry$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ③ | step 1 and step 2 |

`FullAdder · output · output matches specification`
