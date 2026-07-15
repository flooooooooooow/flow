# full_adder

*The full adder output matches binary addition with carry.*

**Source.** patterson — Patterson & Hennessy, *Computer Organization and Design*, §A.5

## Derived fact 1 — Correct

**Coordinate.** FullAdder · output · output matches specification · **Derived fact**

> **Goal.** We're showing that result.Sum equals expected.the conjunction of sum and result.Cout equals expected.carry.
>
> $$\forall A \in bit,\; result.Sum = expected.sum \land result.Cout = expected.carry$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | Let result = FullAdder(A, B, Cin). |  |  |
| ② | Let expected = binary_add_1bit(A, B, Cin). |  |  |
| ③ | From ① and ②, this implies result.Sum equals expected.the conjunction of sum and result.Cout equals expected.carry. Hence proven. | ③ | $result.Sum = expected.sum \land result.Cout = expected.carry$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ③ | ① and ② |

`FullAdder · output · output matches specification`

## Derived fact 2 — Correct

**Coordinate.** Ripple4 · output · output matches specification · **Derived fact**

> **Goal.** We're showing that sum equals expected.
>
> $$\forall A \in bit,\; sum = expected$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | Let carry = Cin. |  |  |
| ② | Let step = FullAdder(A[i], B[i], carry). |  |  |
| ③ | We invoke the derived fact governing output on FullAdder: the law that output matches specification, for output on FullAdder (instantiated for A[i], B[i], carry). |  |  |
| ④ | Let sum = bits_to_int(s) + bits_to_int(carry) * 16. |  |  |
| ⑤ | Let expected = bits_to_int(A) + bits_to_int(B) + int(Cin). |  |  |
| ⑥ | From ①, ②, ③, ④, and ⑤, this implies sum equals expected. Hence proven. | ⑥ | $sum = expected$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ⑥ | ①, ②, ③, ④, and ⑤ |

`Ripple4 · output · output matches specification`
