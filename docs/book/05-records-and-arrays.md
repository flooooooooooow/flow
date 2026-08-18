# 5. Records and fixed arrays

Primitive values describe one quantity. Structs group related quantities;
arrays store repeated values of one type.

## 5.1 Struct declarations and literals

```flow
struct Sample {
    time_ms: i32,
    value: f64
}
```

The declaration defines a type. A struct literal constructs a value of that
type:

```flow preamble=tests/fixtures/doc_preambles/book-05-records.flow
let first: Sample = Sample { time_ms: 0, value: 1.0 }
```

Fields are selected with `.`:

```flow preamble=tests/fixtures/doc_preambles/book-05-records.flow
let t: i32 = first.time_ms
let measurement: f64 = first.value
```

A mutable struct permits field assignment:

```flow preamble=tests/fixtures/doc_preambles/book-05-records.flow
let mut current: Sample = Sample { time_ms: 0, value: 0.0 }
current.time_ms = 10
current.value = 1.25
```

## 5.2 Fixed arrays

`array<T, N>` contains exactly `N` elements of type `T`:

```flow
let values: array<i32, 4> = [10, 20, 30, 40]
```

Indices begin at zero. The valid indices above are `0`, `1`, `2`, and `3`.
The natural traversal is therefore:

```flow preamble=tests/fixtures/doc_preambles/book-05-records.flow
for i in 0 to 4 {
    print(values[i])
}
```

Mutation requires the array binding to be mutable:

```flow
let mut values: array<i32, 4> = [10, 20, 30, 40]
values[1] = 25
```

## 5.3 Arrays of records

```flow preamble=tests/fixtures/doc_preambles/book-05-records.flow
let samples: array<Sample, 4> = [
    Sample { time_ms: 0,  value: 1.0 },
    Sample { time_ms: 10, value: 1.5 },
    Sample { time_ms: 20, value: 2.0 },
    Sample { time_ms: 30, value: 2.5 }
]
```

Indexing and field selection compose:

```flow preamble=tests/fixtures/doc_preambles/book-05-records.flow
let third_value: f64 = samples[2].value
```

## 5.4 Reduction

A reduction converts a collection into one summary value. Summation is the
standard example:

```flow
struct Sample {
    time_ms: i32,
    value: f64
}

function mean4(samples: array<Sample, 4>) -> f64 {
    let mut total: f64 = 0.0
    for i in 0 to 4 {
        total = total + samples[i].value
    }
    return total / 4.0
}
```

The accumulator invariant after `i` iterations is:

```text
total = samples[0].value + ... + samples[i - 1].value
```

At termination `i == 4`, so `total` contains all four values.

## 5.5 Complete demonstration

```flow
extern {
    function printf(fmt: string, ...) -> i32
}

struct Sample {
    time_ms: i32,
    value: f64
}

function mean4(samples: array<Sample, 4>) -> f64 {
    let mut total: f64 = 0.0
    for i in 0 to 4 {
        total = total + samples[i].value
    }
    return total / 4.0
}

function main() -> i32 {
    let mut samples: array<Sample, 4> = [
        Sample { time_ms: 0, value: 1.0 },
        Sample { time_ms: 10, value: 1.5 },
        Sample { time_ms: 20, value: 2.0 },
        Sample { time_ms: 30, value: 2.5 }
    ]

    samples[3].value = 3.5
    printf("last sample: t=%d value=%.1f\n", samples[3].time_ms, samples[3].value)
    printf("mean: %.3f\n", mean4(samples))
    return 0
}
```

Source:
[`examples/book/05_records_arrays.flow`](../../examples/book/05_records_arrays.flow)

```bash
./flow run examples/book/05_records_arrays.flow
```

```text
last sample: t=30 value=3.5
mean: 2.000
```

## 5.6 Shape belongs in the type

The length in `array<Sample, 4>` is part of the type. A function accepting that
type has a compile-time guarantee that four elements exist. The same function
does not accept an array of five elements.

When a function must operate on several lengths without copying, use a span.
A span is a borrowed view consisting conceptually of a pointer and a length.
Spans belong to the systems portion of the book because their validity depends
on the storage they view.

## Exercises

1. Define `Point { x: f64, y: f64 }` and compute squared distance from the
   origin.
2. Find the maximum value in an `array<i32, 8>`.
3. Add `quality: i32` to `Sample` and average only samples with positive
   quality.
4. State the accumulator invariant for the maximum algorithm.

Next: [Pipelines and explicit results](06-pipelines-and-results.md).

