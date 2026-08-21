# 9. Expressions, matching, and declarative operations

An expression produces a value. A statement changes control or program state.
Flow includes ordinary operators, value-producing conditionals, closures,
pattern matching, loop control, deferred cleanup, and declarative operations.

## 9.1 Operators and precedence

From highest to lowest precedence:

1. parentheses;
2. field and index selection, `.` and `[]`;
3. unary `!`, `not`, `-`, address-of `&`, and dereference `*`;
4. `*`, `/`, `%`;
5. `+`, `-`;
6. `<`, `>`, `<=`, `>=`;
7. `==`, `!=`;
8. `&&` or `and`;
9. `||` or `or`.

Bit operations are available on integer values:

```flow preamble=tests/fixtures/doc_preambles/book-09-values.flow
let read: i32 = 1
let write: i32 = 2
let execute: i32 = 4
let permissions: i32 = read | write
let can_write: bool = (permissions & write) != 0
let shifted: i32 = execute << 3
let toggled: i32 = permissions ^ write
let inverted: i32 = ~permissions
```

## 9.2 Built-in operations

The compiler recognises ordinary output and numeric helpers including
`print`, `println`, `printf`, `length`, `sqrt`, `sin`, `cos`, `abs`, `min`,
and `max`. More extensive math, string, collection, and platform operations
come from the standard library or an `extern` declaration.

## 9.3 Value-producing `if`

```flow preamble=tests/fixtures/doc_preambles/book-09-values.flow
let magnitude: i32 = if n >= 0 { n } else { -n }
```

Both arms are expressions and `else` is required. Their types must be
compatible. The C backend lowers the form to a conditional expression; MLIR
uses a value-producing `scf.if`.

## 9.4 Closures

```flow preamble=tests/fixtures/doc_preambles/book-09-values.flow
function apply(f: (i32) -> i32, x: i32) -> i32 {
    return f(x)
}

function make_adder(n: i32) -> (i32) -> i32 {
    return |x: i32| -> i32 { return x + n }
}

let add5: (i32) -> i32 = make_adder(5)
let result: i32 = apply(add5, 37)
```

Free variables are captured by value when the closure is created. A later
mutation of the original local does not change the captured snapshot. The C
backend represents a capturing closure as a function pointer plus an
environment; escaping environments are copied to heap storage.

```bash
FLOW_HOST=python ./flow run tests/lang/test_closures.flow
```

The MLIR backend does not implement capturing closures.

## 9.5 Worked closure: capture by value

The next program captures `base` while its value is `10`. Changing the local
variable afterwards does not change the closure's private copy.

```flow preamble=tests/fixtures/doc_preambles/book-09-values.flow
extern {
    function printf(fmt: string, ...) -> i32
}

function apply(f: (i32) -> i32, value: i32) -> i32 {
    return f(value)
}

function main() -> i32 {
    let mut base: i32 = 10
    let add_base: (i32) -> i32 = |value: i32| -> i32 {
        return value + base
    }

    base = 100
    let result: i32 = apply(add_base, 5)

    printf("captured result: %d\n", result)
    if result != 15 { return 1 }
    return 0
}
```

Source:
[`examples/book/11_closure_snapshot.flow`](../../examples/book/11_closure_snapshot.flow)

```bash
FLOW_HOST=python ./flow run examples/book/11_closure_snapshot.flow
```

```text
captured result: 15
```

The type annotation on `add_base` records the closure signature. `apply`
accepts any closure with that signature. The exit check also proves that the
later assignment `base = 100` did not alter the captured value.

## 9.6 Match arms

```flow preamble=tests/fixtures/doc_preambles/book-09-values.flow
function describe(n: i32) -> string {
    match n {
        0 => { return "zero" }
        1 | 2 | 3 => { return "small" }
        x if x < 0 => { return "negative" }
        _ => { return "other" }
    }
}
```

Arms are tested in source order. A guard that evaluates false continues to the
next arm. `_` is a wildcard; a bare identifier binds the matched value.

Struct and fixed-list patterns destructure values:

```flow preamble=tests/fixtures/doc_preambles/book-09-values.flow id=point-type
struct Point {
    x: i32,
    y: i32
}

let point: Point = Point { x: 0, y: 0 }

match point {
    Point(0, 0) => { println("origin") }
    Point(0, y) => { print(y) }
    Point(x, y) if x == y => { println("diagonal") }
    default { println("general") }
}

let samples: array<i32, 3> = [0, 2, 3]

match samples {
    [0, second, third] => { print(second + third) }
    default { println("different shape") }
}
```

Literal, Boolean, enum, float, string, struct, list, binding, wildcard,
alternation, and guarded patterns are implemented. Exhaustiveness analysis is
substantial for Boolean and enum variants and deliberately limited for open
integer domains. See
[`tests/lang/test_match_patterns.flow`](../../tests/lang/test_match_patterns.flow).

One backend edge remains: `break` inside a C-lowered match arm can leave the C
`switch` rather than the enclosing loop. Avoid that shape when C/MLIR parity
is required.

## 9.7 Loop exits and deferred cleanup

```flow preamble=tests/fixtures/doc_preambles/book-09-values.flow
while active {
    if should_skip() {
        continue
    }
    if should_stop() {
        break
    }
    process()
}
```

`continue` begins the next iteration; `break` exits the nearest loop.

`defer` schedules cleanup for the current scope:

```flow preamble=tests/fixtures/doc_preambles/book-09-values.flow
let buffer: ptr<u8> = malloc(1024)
if buffer == null { return 1 }
defer free(buffer)

use_buffer(buffer)
return 0  # free runs before the return completes
```

Deferred actions run in reverse declaration order when control leaves the
scope, including an early return.

## 9.8 Data-parallel loops

```flow preamble=tests/fixtures/doc_preambles/book-09-values.flow
parallel for i in 0 to n {
    output[i] = input[i] * 2.0
}
```

The C backend emits an OpenMP loop when the compiler supports OpenMP and a
correct serial loop otherwise. Iterations must not race on shared mutable
state. MLIR represents the loop with `scf.parallel`, but its present lowering
pipeline executes serially.

```bash
./flow run examples/concurrency/parallel_for.flow
```

## 9.9 Declarative ordering and search

```flow ignore="catalogue of ordering forms over illustrative collections"
values |> sort
values |> sort descending
players |> sortBy [desc .score, asc .name]
values |> sort unique
let position: i32 = values |> find(target)
```

The source states the required result. The compiler chooses among registered
plans using applicability constraints, ordering hints, scratch-space
requirements, and a cost model. Hints can permit a no-op, reversal, counting
sort, or binary search. `stable` and `unstable` parse, but current plans are all stable.
GPU, SIMD, entropy, and compact ordering modifiers parse without specialised
implementations.

Inspect a decision:

```bash
./flow explain examples/basics/declarative_sort.flow
```

## 9.10 Fork and choose pipelines

Both forms below collect results into a record or select among branches, so
they need a record to fill and something to choose between:

```flow id=fork-types
struct Stats {
    doubled: i32,
    squared: i32,
    plus_ten: i32
}

enum Mode { Double, Triple }

function twice(x: i32) -> i32 { return x * 2 }
function square(x: i32) -> i32 { return x * x }
function add(x: i32, k: i32) -> i32 { return x + k }
function double(x: i32) -> i32 { return x * 2 }
function triple(x: i32) -> i32 { return x * 3 }
function normalize(x: i32) -> i32 { return x }
```

A fork evaluates one source once and sends it into several branches:

```flow preamble=tests/fixtures/doc_preambles/book-09-values.flow uses=fork-types
let stats: Stats = n |> Stats {
    doubled = twice,
    squared = square,
    plus_ten = add(_, 10),
}
```

An anonymous fork infers its record shape. `choose` selects a branch from
state and permits the selected result to continue through the pipeline:

```flow preamble=tests/fixtures/doc_preambles/book-09-values.flow uses=fork-types
let mode: Mode = Mode { tag: Mode_Double }

let result = input
    |> choose mode.tag {
        Mode_Double => double,
        Mode_Triple => triple,
    }
    |> normalize
```

Run the complete demonstrations:

```bash
FLOW_HOST=python ./flow run examples/basics/pipeline_fork.flow
FLOW_HOST=python ./flow run examples/basics/pipeline_fork_inferred.flow
FLOW_HOST=python ./flow run examples/basics/pipeline_choose.flow
```

## Exercises

1. Pack four Boolean settings into an integer and recover each setting.
2. Use a guarded match to classify negative, small, and large values.
3. Write a closure that captures two coefficients of a linear function.
4. Compare the plan selected for sorted and unsorted integer data with
   `flow explain`.

Next: [Memory, spans, and lifetime domains](10-memory-and-lifetimes.md).
