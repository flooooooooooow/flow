# 5. Records and fixed arrays

Primitive values describe one quantity. Structs group related quantities; arrays store repeated values of one type. Every `flow` block in this chapter is compiler-checked in CI.

## 5.1 Struct declarations and literals

```flow
struct Sample {
    time_ms: i32,
    value: f64
}
```

A struct literal constructs a value of that type and fields are selected with `.`:

```flow
struct SampleRead {
    time_ms: i32,
    value: f64
}

function first_measurement() -> f64 {
    let first: SampleRead = SampleRead { time_ms: 0, value: 1.0 }
    let t: i32 = first.time_ms
    if t == 0 {
        return first.value
    }
    return 0.0
}
```

A mutable struct permits field assignment:

```flow
struct MutableSample {
    time_ms: i32,
    value: f64
}

function updated_sample() -> f64 {
    let mut current: MutableSample = MutableSample { time_ms: 0, value: 0.0 }
    current.time_ms = 10
    current.value = 1.25
    return current.value
}
```

## 5.2 Fixed arrays

`array<T, N>` contains exactly `N` elements of type `T`:

```flow
function second_value() -> i32 {
    let values: array<i32, 4> = [10, 20, 30, 40]
    return values[1]
}
```

Indices begin at zero. The natural traversal is:

```flow
function sum_values() -> i32 {
    let values: array<i32, 4> = [10, 20, 30, 40]
    let mut total: i32 = 0
    for i in 0 to 4 {
        total = total + values[i]
    }
    return total
}
```

Mutation requires a mutable binding:

```flow
function mutate_array() -> i32 {
    let mut values: array<i32, 4> = [10, 20, 30, 40]
    values[1] = 25
    return values[1]
}
```

## 5.3 Arrays of records

```flow
struct TimedSample {
    time_ms: i32,
    value: f64
}

function third_sample_value() -> f64 {
    let samples: array<TimedSample, 4> = [
        TimedSample { time_ms: 0, value: 1.0 },
        TimedSample { time_ms: 10, value: 1.5 },
        TimedSample { time_ms: 20, value: 2.0 },
        TimedSample { time_ms: 30, value: 2.5 }
    ]
    return samples[2].value
}
```

## 5.4 Reduction

A reduction converts a collection into one summary value:

```flow
struct ReducedSample {
    time_ms: i32,
    value: f64
}

function mean4(samples: array<ReducedSample, 4>) -> f64 {
    let mut total: f64 = 0.0
    for i in 0 to 4 {
        total = total + samples[i].value
    }
    return total / 4.0
}
```

After `i` iterations, the accumulator contains the sum of elements `0` through `i - 1`; at termination it contains all four values.

## 5.5 Complete demonstration

```flow from=examples/book/05_records_arrays.flow
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

Source: [`examples/book/05_records_arrays.flow`](../../examples/book/05_records_arrays.flow)

```bash
FLOW_HOST=python ./flow run examples/book/05_records_arrays.flow
```

## 5.6 Shape belongs in the type

The length in `array<Sample, 4>` is part of the type. A function accepting that type has a compile-time guarantee that four elements exist. When a function must operate on several lengths without copying, use a `span<T>` borrowed view.

## Exercises

Define a `Point` and compute squared distance from the origin; find the maximum in an `array<i32, 8>`; add a quality field and average only valid samples; then state the accumulator invariant for the maximum algorithm.

Next: [Pipelines and explicit results](06-pipelines-and-results.md).
