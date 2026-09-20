# Rosetta Code tasks in Flow

Canonical [Rosetta Code](https://rosettacode.org) tasks written in Flow. Each
program is a single file with a `function main() -> i32` that prints the
expected output. They exist as the source material for a Flow entry on Rosetta
Code.

## Running

Compile and run any task with the driver. The default compiler host is the
Stage-A subset, which rejects the full language, so set `FLOW_HOST=python`:

```
FLOW_HOST=python ./flow-driver run examples/rosetta/fizzbuzz.flow
```

Swap the filename for any task below.

## Tasks

| Task | File | Rosetta task |
| --- | --- | --- |
| FizzBuzz | `fizzbuzz.flow` | FizzBuzz |
| Factorial | `factorial.flow` | Factorial |
| Fibonacci sequence | `fibonacci-sequence.flow` | Fibonacci sequence |
| Greatest common divisor | `greatest-common-divisor.flow` | Greatest common divisor |
| Sieve of Eratosthenes | `sieve-of-eratosthenes.flow` | Sieve of Eratosthenes |
| Quicksort | `quicksort.flow` | Sorting algorithms/Quicksort |
| Binary search | `binary-search.flow` | Binary search |
| Reverse a string | `string-reversal.flow` | Reverse a string |
| Ackermann function | `ackermann-function.flow` | Ackermann function |
| Towers of Hanoi | `towers-of-hanoi.flow` | Towers of Hanoi |
| 100 doors | `hundred-doors.flow` | 100 doors |

## Tests

`tests/unit/test_rosetta_examples.py` parses and generates C for every file
here, so the examples stay green as the compiler changes.
