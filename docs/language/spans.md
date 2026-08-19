# Spans: borrowed views over contiguous storage

> **Status:** the concrete-element layer is implemented in the C backend.
> `span<T>`, `span<mut T>`, `span<T, N>` and the `&[T]` sugar all work today.
> Inference (bare `span`, `span<mut>`, `span<number>`, dependent extents) is
> not implemented and the parser says so. See the staging table at the end.

A span is a borrowed view over contiguous elements. It never owns its data,
never allocates, and never outlives the storage it points at. The design goal
is that **callers never write `span(...)`** — any contiguous value borrows
into a span automatically, while element type, extent, mutability, and
lifetime stay visible to the compiler.

## The problem it replaces

Without spans, a function that works over a run of floats has to pick one of
these, and each one is wrong in a different way:

```flow
function analyse(samples: ptr<f32>, n: i32) -> f32   # length can lie
function analyse(samples: array<f32, 512>) -> f32    # one extent only
function analyse(samples: Vec) -> f32                # forces a container
```

The pointer-and-length pair is the honest shape of the data, so the language
should carry it as one thing and check it.

## Declaring

Name the element type, and add an extent where the function depends on one:

```flow
function sum(values: span<f64>) -> f64 { }         # immutable view
function clear(values: span<mut i32>) { }          # mutable view
function processBlock(samples: span<f32, 512>) { } # static extent
```

`span<const T>` is accepted as an explicit spelling of `span<T>`.

Bare `span`, `span<mut>`, `span<const>`, `span[16]`, `span<number>`, and
dependent extents like `span<mut, source.extent>` are part of the design but
are not implemented. The parser rejects each one by name:

```text
error: bare `span` with inferred element type is not yet implemented in this
       compiler version
  Hint: name the element type, e.g. span<f32> or &[f32]
```

## Reading and writing through a span

A span exposes its length as `.len` (an `i64`) and its elements by index.
`len(values)` is accepted and means the same thing; `.len` is the canonical
spelling.

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

Writing through a view requires `span<mut T>`:

```flow
function clear(values: span<mut i32>) {
    let mut i: i32 = 0
    while i < values.len {
        values[i] = 0
        i = i + 1
    }
}
```

```text
error: cannot write through `values`: span<i32> is an immutable view
       (declare it span<mut i32>)
```

## Reference sugar

The bracket forms are sugar for the same semantic type:

| Sugar | Semantic type |
|---|---|
| `&[T]` | `span<const T>` |
| `&mut [T]` | `span<mut T>` |
| `&[T; N]` | `span<const T, N>` |
| `&mut [T; N]` | `span<mut T, N>` |

The sugar is desugared in the parser, so the two spellings produce one
internal type and are interchangeable everywhere:

```flow
function analyse(samples: span<f32>) -> f32
function analyse(samples: &[f32]) -> f32        # identical signature
function fft(frame: &[f32; 1024])
```

## Calling

Contiguous sources borrow implicitly. No wrapper, no cast:

```flow
let signal: array<f32, 512> = ...

analyse(signal)            # {signal, 512}
analyse(signal[4..12])     # {&signal[4], 8}
analyse(window)            # another span, passed through
```

A slice expression produces a span directly:

```flow
let middle: span<f32> = samples[128..256]
```

Bounds are ordinary expressions and may be runtime values. Literal bounds on
a fixed array give the slice a compile-time extent, which is what makes a
`span<T, N>` parameter checkable.

Three sources borrow; everything else is an error:

| Source | Result |
|---|---|
| `array<T, N>` variable | `{ arr, N }` |
| slice `a[i..j]` | `{ &a[i], j - i }` |
| another span of the same element | passed through |
| `ptr<T>` | rejected — a pointer has no length |

```text
error: cannot borrow ptr<f32> into span<f32> for parameter 'values' of
       'analyse': a pointer has no length. Slice it instead, e.g. `p[0..n]`
```

Slicing supplies the missing length, so `analyse(p[0..n])` is fine.

## Static extent

A `span<T, N>` parameter checks the source length at the call site:

```text
error: static extent mismatch: parameter 'values' of 'matrix4' expects
       span<f32, 16> but the argument has length 4 (expected 16, got 4)
```

A source whose length is only known at runtime cannot form a static-extent
span at all:

```text
error: static extent mismatch: parameter 'values' of 'matrix4' expects
       span<f32, 16>, but the argument length is not known at compile time;
       a static-extent span cannot be formed from a dynamic length
```

## Lifetime

A span may not outlive its storage:

```flow expect-error
function invalid() -> span<i32> {
    let local: array<i32, 3> = [1, 2, 3]
    return local[0..3]
}
```

```text
error: span outlives borrowed storage `local` at line 3, column 5
```

The same check rejects assigning such a view to a module static, which
outlives every frame.

**What this catches, and what it does not.** This is a scope-local check, not
region inference. It catches a `return` of a local array or of a span local
that borrows one, transitively through slice expressions, and the same value
assigned to a module static. It does **not** track borrows through struct
fields, closure environments, function calls that launder a view, or pointers
taken out of a span. Those escapes compile today and are unsound; treat them
as a known gap until layer 2 lands.

**With lifetime domains.** [Lifetime domains](lifetime-domains.md) generalise
this check. A function annotated `@lifetime(callback)` or `@lifetime(frame)`
gets the same escape analysis over pointers as well as spans, and its
diagnostic names both domains instead of just the storage:

```text
error: lifetime domain escape: `scratch` lives in the `callback` domain but is
       stored in `tail`, which lives in the `application` domain (a
       longer-lived domain may not hold a reference to a shorter-lived one)
```

Where both checks apply to one assignment or return, only the domain
diagnostic is emitted. Without an annotation nothing changes: the span message
above is what you get. The two share their gaps exactly, since the domain
checker is built on `_span_origin` and `_function_local_storage`.

## Mutability

`span<mut T>` may only borrow storage declared `let mut`. Borrowing a `let`
binding mutably is an error at the call site, naming the binding:

```text
error: cannot borrow `samples` mutably; it is declared with `let`
```

`span<const T>` borrows from either. A `span<mut T>` may be passed where a
`span<const T>` is expected; the reverse is rejected.

## Lowering

A span is a two-word value, not a heap object:

```c
typedef struct { const float *data; int64_t len; } flow_span_const_f32;
typedef struct { float       *data; int64_t len; } flow_span_mut_f32;
```

One typedef is emitted per (element, mutability) pair actually used by the
program. Static extents keep the same representation so one function body
serves both; the extent is a compile-time fact used for checking, and a
`span<T, N>` argument is checked against the source length at the call site.

A whole function, source and generated C (the per-access bounds check on
`values[i]` is elided here for readability; it compares the index against
`values.len`):

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
```

```c
typedef struct { const int32_t *data; int64_t len; } flow_span_const_i32;

int32_t total_span_const_i32(flow_span_const_i32 values) {
    int32_t acc = 0;
    int32_t i = 0;
    while (i < values.len) {
        acc = (acc + (values).data[i]);
        i = (i + 1);
    }
    return acc;
}
```

Calling it with a fixed array borrows in place:

```c
total_span_const_i32(((flow_span_const_i32){ .data = (const int32_t*)(xs), .len = (int64_t)4 }))
```

and a slice becomes a pointer offset:

```c
total_span_const_i32(((flow_span_const_i32){ .data = (const int32_t*)(((xs)) + (2)), .len = (int64_t)((5) - (2)) }))
```

## Staging

| Capability | Status |
|---|---|
| `span<T>` / `span<mut T>` concrete element types | ✅ C backend |
| `span<const T>` explicit spelling | ✅ C backend |
| `&[T]` / `&mut [T]` sugar | ✅ parse-time desugar |
| Auto-borrow from fixed arrays and slices | ✅ C backend |
| Span-to-span pass-through (`mut` to `const` narrowing) | ✅ C backend |
| Slice expressions producing spans | ✅ literal and runtime bounds |
| Static extent `span<T, N>` / `&[T; N]` with length checking | ✅ C backend |
| `.len` and `len(s)` | ✅ C backend |
| Element read / write through a span | ✅ write requires `span<mut T>` |
| Pointer arguments rejected (no length) | ✅ |
| Escape checking (`span outlives borrowed storage`) | ⚠️ direct cases only — see [Lifetime](#lifetime) |
| Spans in the MLIR / JS / Python backends | ❌ C backend only |
| Bare `span` with full inference | ❌ layer 2 |
| `span<mut>` / `span<const>` without an element type | ❌ layer 2 |
| Dependent extents (`span<mut, source.extent>`) | ❌ layer 2 |
| `span<number>` and other trait-shaped element constraints | ❌ layer 2 |
| Span methods (`fill`, `reduce`, iteration) | ❌ layer 2 |
| Spans as struct fields | ⚠️ compiles, but no escape checking — avoid |

The four layer-2 spellings (`span`, `span<mut>` / `span<const>`,
`span<number>`, `span<mut, source.extent>`, plus `span[N]`) are rejected at
parse time with a message saying they are not implemented in this compiler
version.

Example: [examples/basics/spans.flow](../../examples/basics/spans.flow) ·
Tests: `tests/lang/test_spans.flow`, `tests/unit/test_spans.py`

Related: [types.md](types.md) ·
[lifetime-domains.md](lifetime-domains.md) ·
[LANGUAGE_SPEC](../LANGUAGE_SPEC.md)
