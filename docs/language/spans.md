# Spans: borrowed views over contiguous storage

> **Status:** `span<T>`, `span<mut T>`, `span<T, N>` and the `&[T]` / `&mut [T]` sugar are implemented in the C backend.

A span is a borrowed `{pointer, length}` view over contiguous elements. It never owns its data and never allocates. Every `flow` block on this page is compiler-checked in CI; rejection examples are `flow expect-error` tests.

## Why spans exist

A raw pointer does not carry a length, while a fixed array bakes one exact extent into the parameter type. A span carries the pointer and length together:

```flow
function first_sample(samples: span<f32>) -> f32 {
    return samples[0]
}

function clear_samples(samples: span<mut f32>) -> void {
    let mut i: i32 = 0
    while i < samples.len {
        samples[i] = 0.0
        i = i + 1
    }
}
```

Use `span<T, N>` when the function requires a compile-time extent:

```flow
function first_of_four(samples: span<f32, 4>) -> f32 {
    return samples[0]
}
```

## Reading and writing

A span exposes `.len` and indexed element access:

```flow
function sum(values: span<i32>) -> i32 {
    let mut acc: i32 = 0
    let mut i: i32 = 0
    while i < values.len {
        acc = acc + values[i]
        i = i + 1
    }
    return acc
}
```

Writing requires `span<mut T>`:

```flow
function zero(values: span<mut i32>) -> void {
    let mut i: i32 = 0
    while i < values.len {
        values[i] = 0
        i = i + 1
    }
}
```

## Reference sugar

The parser accepts these equivalent forms:

| Surface type | Semantic type |
|---|---|
| `&[T]` | `span<const T>` |
| `&mut [T]` | `span<mut T>` |
| `&[T; N]` | `span<const T, N>` |
| `&mut [T; N]` | `span<mut T, N>` |

```flow
function analyse_span(samples: span<f32>) -> f32 {
    return samples[0]
}

function analyse_ref(samples: &[f32]) -> f32 {
    return samples[0]
}

function fft_first(frame: &[f32; 4]) -> f32 {
    return frame[0]
}
```

## Borrowing arrays and slices

Fixed arrays and slices borrow into spans at the call site without allocation:

```flow
function total(values: span<i32>) -> i32 {
    let mut acc: i32 = 0
    let mut i: i32 = 0
    while i < values.len {
        acc = acc + values[i]
        i = i + 1
    }
    return acc
}

function array_total() -> i32 {
    let values: array<i32, 4> = [1, 2, 3, 4]
    return total(values)
}

function middle_total() -> i32 {
    let values: array<i32, 6> = [1, 2, 3, 4, 5, 6]
    return total(values[2..5])
}
```

A raw `ptr<T>` cannot be borrowed as a span because the pointer contains no length. Slice the pointer when a length is known.

## Static extents

A `span<T, N>` requires a source whose length is known to be `N`:

```flow
function matrix4_first(values: span<f32, 16>) -> f32 {
    return values[0]
}
```

Passing a fixed array of a different length is rejected at the call site.

## Lifetime

A span may not outlive the storage it borrows:

```flow expect-error
function invalid_view() -> span<i32> {
    let local: array<i32, 3> = [1, 2, 3]
    return local[0..3]
}
```

The same escape analysis rejects storing a view of function-local storage into a module static. [Lifetime domains](lifetime-domains.md) generalise this check and give the storage explicit `callback`, `frame`, `session`, or `application` lifetimes.

The current check is intentionally scope-local. It does not yet follow borrows through arbitrary struct fields, closures, indirect calls, pointer laundering, or heap objects.

## Mutability

A `span<mut T>` may borrow mutable storage. An immutable span can borrow either mutable or immutable storage. Passing an immutable span where a mutable span is required is rejected.

```flow
function overwrite(values: span<mut i32>) -> void {
    values[0] = 42
}

function mutable_source() -> i32 {
    let mut values: array<i32, 3> = [1, 2, 3]
    overwrite(values)
    return values[0]
}
```

## Lowering

A span lowers to a two-word C value conceptually equivalent to a pointer plus `i64` length. Static extents use the same runtime representation; the extent is a compile-time checking fact.

The generated C shape is approximately:

```c
typedef struct { const float *data; int64_t len; } flow_span_const_f32;
typedef struct { float *data; int64_t len; } flow_span_mut_f32;
```

## Deliberately unsupported forms

Bare inferred `span`, `span<mut>` without an element type, `span<number>`, dependent extents such as `span<mut, source.extent>`, and span methods such as `fill`/`reduce` are not current Flow. The parser rejects them rather than silently assigning guessed semantics.

## Staging

| Capability | Status |
|---|---|
| `span<T>` / `span<mut T>` | ✅ C backend |
| `span<const T>` | ✅ C backend |
| `&[T]` / `&mut [T]` | ✅ parse-time sugar |
| Fixed-array and slice auto-borrow | ✅ |
| Span-to-span pass-through | ✅ |
| `span<T, N>` static extent | ✅ |
| `.len` and indexed access | ✅ |
| Direct escape checking | ✅ direct cases |
| MLIR / JS / Python backend spans | ❌ C backend only |
| Fully inferred element types | ❌ |
| Dependent extents | ❌ |
| Span methods | ❌ |

Example: [`examples/basics/spans.flow`](../../examples/basics/spans.flow). Tests: `tests/lang/test_spans.flow`, `tests/unit/test_spans.py`.

A `trait` can abstract APIs that accept or return span-based views; traits do not change span ownership or lifetime rules.

Related: [Types](types.md), [Lifetime domains](lifetime-domains.md), [Language specification](../LANGUAGE_SPEC.md).
