# full_adder

*The full adder output matches binary addition with carry.*

**Source.** patterson — Patterson & Hennessy, *Computer Organization and Design*, §A.5

**Executable.** Bits are `i32` in `{0,1}` with local `xor`/`and`/`or` helpers.
Run the exhaustive smoke test: `./flow run examples/verify/circuits/full_adder.flow`.
Theorem bodies still use English `and` for the verify corpus.

**Surface note.** The runnable example uses `i32` bits in `{0,1}` (with `xor` / `and` / `or` helpers) until a first-class `bit` type lands in codegen. The theorem still uses English `and` and `by exhaustive`; `main` exhaustively checks all 8 input combinations at runtime.

## Derived fact — Correct

**Coordinate.** FullAdder · output · output matches specification · **Derived fact**

> **Goal.** We're showing that `result.Sum == expected.sum` and `result.Cout == expected.carry`.
>
> $$\forall A,B,C_{in} \in \{0,1\},\; result.Sum = expected.sum \land result.Cout = expected.carry$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | Let result = FullAdder(A, B, Cin). |  |  |
| ② | Let expected = binary_add_1bit(A, B, Cin). |  |  |
| ③ | From ① and ②, this implies result.Sum equals expected.sum and result.Cout equals expected.carry (by exhaustive). Hence proven. | ③ | $result.Sum = expected.sum \land result.Cout = expected.carry$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ③ | ① and ② |

`FullAdder · output · output matches specification`
