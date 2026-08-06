# Spans: borrowed views over contiguous storage

> **Status:** design accepted, implementation in progress. Rows marked
> "planned" below are not in the compiler yet; see the staging table at the
> end for what is live.

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

The bare form infers everything:

```flow
function process(values: span) {
    # values.element    inferred
    # values.extent     inferred
    # values.mutability inferred
}
```

Constraints are added only where the function actually depends on them:

```flow
function clear(values: span<mut>) {
    values.fill(0)
}

function sum(values: span<number>) -> number {
    return values.reduce(+)
}

function transform(input: span<const T>, output: span<mut T>) { }

function matrix4(values: span[16]) { }          # static extent
function processBlock(samples: span<f32, 512>) { }
```

Generic code can bind the properties by name when it needs to relate them:

```flow
function copy<T, N>(source: span<const T, N>, destination: span<mut T, N>) {
    destination = source
}
```

but most code should not have to:

```flow
function copy(source: span<const>, destination: span<mut, source.extent>) {
    destination = source
}
```

## Reference sugar

The bracket forms are sugar for the same semantic type:

| Sugar | Semantic type |
|---|---|
| `&[T]` | `span<const T>` |
| `&mut [T]` | `span<mut T>` |
| `&[T; N]` | `span<const T, N>` |
| `&mut [T; N]` | `span<mut T, N>` |

Both spellings are supported and interchangeable:

```flow
function analyse(samples: span<f32>) -> f32
function analyse(samples: &[f32]) -> f32        # identical signature
function fft(frame: &[complex; 1024])
```

## Calling

Contiguous sources borrow implicitly. No wrapper, no cast:

```flow
process(vector)
process(array)
process(buffer)
process(data[4..12])

matrix4(float[16])
matrix4(vector.withLength(16))
matrix4(buffer[0..16])
```

A slice expression produces a span directly:

```flow
let middle = samples[128..256]      # span<mut f32, 128>
```

Non-contiguous sources are **not** silently materialised. Converting costs an
allocation, so it is written out:

```flow
process(items.filter(valid).collect())
```

## Lifetime

A span may not outlive its storage:

```flow
function invalid() -> span {
    let local = [1, 2, 3]
    return local
}
```

```text
error: span outlives borrowed storage `local`
  --> invalid.flow:3:12
   |
 2 |     let local = [1, 2, 3]
   |         ----- storage dropped at end of function
 3 |     return local
   |            ^^^^^ borrowed view escapes here
```

The same check rejects storing a span into a longer-lived location (a module
static, a struct field that outlives the borrow, a captured closure
environment).

## Mutability

`span<mut T>` may only borrow from mutable storage. Borrowing a `let` binding
mutably is an error at the call site, naming the binding:

```text
error: cannot borrow `samples` mutably; it is declared with `let`
```

`span<const T>` borrows from either.

## Lowering

A span is a two-word value, not a heap object:

```c
typedef struct { const float *data; int64_t len; } flow_span_const_f32;
typedef struct { float       *data; int64_t len; } flow_span_mut_f32;
```

Static extents keep the same representation so one function body serves both;
the extent is a compile-time fact used for checking and optimisation, and a
`span<T, N>` argument carries a compile-time assertion that the source length
is exactly `N`.

## Staging

| Capability | Status |
|---|---|
| `span<T>` / `span<mut T>` concrete element types | planned |
| `&[T]` / `&mut [T]` sugar | planned |
| Auto-borrow from fixed arrays and slices | planned |
| Slice expressions producing spans | planned |
| Static extent `span<T, N>` / `&[T; N]` with length checking | planned |
| Escape checking (`span outlives borrowed storage`) | planned |
| Bare `span` with full inference | planned |
| Dependent extents (`span<mut, source.extent>`) | planned |
| `span<number>` and other trait-shaped element constraints | planned |
| Span methods (`fill`, `reduce`, iteration) | planned |

Related: [types.md](types.md) · [LANGUAGE_SPEC](../LANGUAGE_SPEC.md)
