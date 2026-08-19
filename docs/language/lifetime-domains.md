# Lifetime domains

> **Status:** v0 is implemented in the C-backend type checker. Domains are
> declared with `@lifetime(...)` on functions and module statics. Four rules
> are enforced (see [What the compiler checks](#what-the-compiler-checks)).
> Everything the checker cannot decide soundly is listed under
> [What the compiler does not check](#what-the-compiler-does-not-check) and is
> not half-checked.

A real-time program does not have one memory. It has several, each with a
different clock:

| Domain | Lives for | Typical storage |
|---|---|---|
| `callback` | one audio block or one render callback | stack locals, caller-provided buffers |
| `frame` | one frame of a loop | a bump arena, reset wholesale at the frame boundary |
| `session` | one document, one stream, one connection | pooled or resettable region |
| `application` | the whole process run | module statics, long-lived heap |

"Stack vs heap" describes where the allocator put the bytes. A lifetime domain
describes when the bytes stop being valid, which is the thing the programmer
actually reasons about and the thing that goes wrong.

Flow already had two halves of this. `@rt_safe` (see
[rt-safety.md](../library/rt-safety.md)) forbids heap traffic in a call chain.
`Arena` in [`lib/stdlib/memory.flow`](../library/memory.md) implements frame
allocation by hand. Neither ties a *value* to a domain, and nothing stopped a
callback-lifetime pointer from being parked in a module static that outlives
every callback.

This is the design from [issue #148](https://github.com/flooooooooooow/flow/issues/148),
kernel-sized: annotations plus checking, no ownership lattice.

## The domain order

```text
callback  <  frame  <  session  <  application
```

Read `<` as "lives no longer than". A `callback` value is dead by the time the
next block starts. An `application` value is alive until the process exits.
The single rule the whole design rests on:

> A longer-lived domain may not hold a reference to a shorter-lived one.

Axiom §7 also names `request` and `persistent`. They are not implemented; see
[Future work](#future-work).

## Declaring a domain

`@lifetime(D)` on a function declares the domain its frame runs in:

```flow
@lifetime(callback)
function process_block(state: ptr<FilterState>, n: i32) -> void {
    # ...
}
```

`@lifetime(D)` on a module static declares the domain of that storage:

```flow
@lifetime(application)
let mut cache: span<f32> = null
```

Those are the only two places a domain is written in v0. This is the
"annotation-only" answer to the open question in the issue: no `domain frame
{ ... }` blocks, no per-`let` annotations, no domains in types. See
[Questions.md](../../Questions.md).

## How a value gets its domain

Inferred from its allocation site. Nothing else.

| Storage | Domain |
|---|---|
| a local declared in a `@lifetime(D)` function | `D` |
| a local declared in an unannotated function | none — unchecked |
| a module static | its `@lifetime(...)`, defaulting to `application` |
| a `const` | `application` |
| memory from `malloc` / `alloc_*` | `application` (it is yours until you free it) |
| memory from `arena_alloc` / `frame_alloc_*` | the arena's own domain, which v0 does not track |

An unannotated function has no domain, so no domain rule fires inside it. The
whole feature is opt-in; adding `@lifetime(...)` to one function does not
change the meaning of any other.

## What the compiler checks

Four rules. Each one is a hard error in `--strict` and a printed warning in
`--lenient`, like every other type-checker diagnostic.

### LD1 — a shorter-lived value may not be stored in a longer-lived static

Inside a `@lifetime(D)` function, assigning a reference rooted in
function-local storage to a module static whose domain outlives `D`:

```text
@lifetime(application)
let mut tail: span<f32> = null

@lifetime(callback)
function process(input: span<f32>) -> void {
    let scratch: array<f32, 64> = [0.0; 64]
    tail = scratch[0..64]
}
```

```text
error: lifetime domain escape: `scratch` lives in the `callback` domain but is
       stored in `tail`, which lives in the `application` domain (a
       longer-lived domain may not hold a reference to a shorter-lived one) at
       line 8, column 5
```

The storage is named, both domains are named, and the position is the
assignment. Compare the span diagnostic it generalises: `span outlives
borrowed storage \`local\``.

### LD2 — a domain function may not return a reference into its own frame

```text
@lifetime(frame)
function build() -> ptr<i32> {
    let scratch: array<i32, 8> = [0; 8]
    return scratch
}
```

```text
error: lifetime domain escape: `scratch` lives in the `frame` domain but is
       returned from 'build', which outlives it (a returned reference may not
       point into the frame that produced it) at line 4, column 5
```

For span returns, the existing span diagnostic (`span outlives borrowed
storage`) already covers this and still fires; LD2 adds the pointer case and
names the domain.

### LD3 — allocation discipline per domain

`@lifetime(callback)` composes with `@rt_safe`: the body, and everything it
calls transitively, must not touch the heap, take a blocking lock, open a
device or file, or submit GPU work. The check is the existing `@rt_safe`
whole-program call graph, so nothing new can slip past it that `@rt_safe`
would have caught.

```text
@lifetime(callback)
function process(n: i32) -> i32 {
    let p: ptr<void> = malloc(64)
    return n
}
```

```text
error: RT-safety violation: 'process' is in the `callback` lifetime domain,
       which forbids allocation, but calls 'malloc', which is forbidden on an
       RT-safe path (heap, device/file I/O, GPU, or blocking lock; see
       docs/language/lifetime-domains.md)
```

Transitive calls report the chain the same way `@rt_safe` does:

```text
error: RT-safety violation: 'process' is in the `callback` lifetime domain,
       which forbids allocation, but calls 'helper', which is not RT-safe
       because it calls 'malloc' (forbidden on an RT-safe path; see
       docs/language/lifetime-domains.md)
```

`@lifetime(frame)` is weaker on purpose. A frame is bump-allocated and reset
wholesale, so bumping is the normal way to allocate there, and a frame loop is
allowed to take a lock. Only creating, destroying or growing heap storage is
forbidden:

```text
error: lifetime domain violation: 'build_scene' is in the `frame` domain but
       calls 'malloc', which allocates or frees heap memory. Frame-domain code
       allocates by bumping a frame arena (frame_alloc_*); see
       docs/language/lifetime-domains.md
```

`arena_alloc`, `arena_alloc_i32`, `arena_alloc_f32`, `arena_reset`,
`arena_used`, `arena_remaining`, `frame_begin`, `frame_end`,
`frame_high_water`, `frame_count` and the `frame_alloc_*` family stay legal in
both `callback` and `frame`, because none of them reaches `malloc`.
`arena_create` / `arena_destroy` / `frame_arena_create` /
`frame_arena_destroy` do, and are rejected.

The two domains differ in exactly one place: a lock. `frame` permits
`mutex_lock`; `callback` does not.

`session` and `application` place no allocation restriction.

### LD4 — a domain may not call into a longer-lived domain

Both functions must be annotated for this to fire. It checks declared intent
against declared intent, so it has no false positives on unannotated code.

```text
@lifetime(session)
function reload_preset(id: i32) -> i32 { return id }

@lifetime(callback)
function process(n: i32) -> i32 {
    return reload_preset(n)
}
```

```text
error: lifetime domain violation: 'process' is in the `callback` domain but
       calls 'reload_preset', which is in the `session` domain (a
       shorter-lived domain may not call into a longer-lived one; see
       docs/language/lifetime-domains.md)
```

The other direction is fine and normal: a `session` function calls a
`callback` function to run one block.

## What the compiler does not check

A lifetime system that misses violations is worse than no lifetime system,
because people trust it. Everything below compiles today and is **not**
checked. None of it is partially checked.

- **Escape through a call.** Passing a local's address to a function that
  stores it is invisible to LD1. Parameters carry no domain in v0, so the
  callee's assignment sees a parameter, not local storage.
- **Escape through a struct field.** Writing a reference into a field of a
  longer-lived struct is not tracked. This is the same gap spans have.
- **Escape through a closure environment**, a function pointer, or dynamic
  dispatch. The `@rt_safe` call graph is over direct named calls only, and LD3
  and LD4 inherit that.
- **Escape through the heap.** `*p = &local` where `p` is `malloc`'d is
  application-domain storage receiving a callback-domain reference, and is not
  caught.
- **Pointer laundering.** Casts, integer round-trips, and pointer arithmetic
  that leaves the tracked expression shapes (variable, slice, address-of,
  field/index under address-of).
- **The domain of arena-allocated memory.** `arena_alloc` returns a pointer
  whose real lifetime is the arena's, not the caller's frame. v0 does not
  model it, so a pointer from a frame arena stored in an application static is
  not rejected.
- **Extern functions.** An `extern` C call is assumed to have no domain and to
  allocate nothing unless it is on the RT-unsafe name list.
- **Cross-module domains.** Annotations are checked within one type-checking
  unit. An imported function's domain is not consulted.

## Interaction with spans

Spans and domains check the same underlying fact from two directions, and the
domain checker is built directly on the span machinery (`_span_origin` and
`_function_local_storage` in `src/flow/type_checker.py`).

- The **span** escape check is always on and needs no annotation. It knows one
  domain boundary: "this function's frame". Its diagnostic is `span outlives
  borrowed storage \`local\``.
- The **domain** escape check is opt-in and names two domains. It fires on the
  same expression shapes plus pointer-typed targets.

Where both apply to one assignment or return, only the domain diagnostic is
emitted, since it strictly says more. A span in a function with no
`@lifetime(...)` still gets the span diagnostic, unchanged.

The two share their known gaps exactly: neither follows a borrow through a
struct field, a call, or a closure. See
[spans.md § Lifetime](spans.md#lifetime).

## Frame domain and the arena

The `frame` domain is wired to the existing bump allocator in
`lib/stdlib/memory.flow`. A `FrameArena` is an `Arena` plus frame bookkeeping:

```text
export struct FrameArena {
    arena: Arena,
    high_water: i64,
    frames: i64
}
```

The API is three calls in the hot path, all bump-pointer arithmetic and all
legal in `callback` and `frame`:

```text
frame_begin(f)            # offset = 0. This is the whole reset.
frame_alloc_f32(f, n)     # offset += n * 4, return the old offset
frame_end(f)              # record high water, count the frame
```

`frame_arena_create` / `frame_arena_destroy` do the one `malloc` and the one
`free`, at startup and shutdown, outside any domain-annotated path.

`frame_begin` is a single store of zero. Freeing a frame's worth of
allocations costs the same as freeing one, which is the point of the domain:

```flow-pseudocode
@lifetime(frame)
function render_frame(f: ptr<FrameArena>, n: i64) -> f32 {
    frame_begin(f)
    let scratch: ptr<f32> = frame_alloc_f32(f, n)
    # ... fill and read scratch ...
    frame_end(f)
    return 0.0
}
```

### Measured cost

`benchmarks/micro/frame_arena_benchmark.flow` runs the same workload twice:
200 frames, 1000 allocations of 64 `f32` per frame, 200,000 allocations, each
block touched at both ends so nothing is optimised away. Apple M-series,
clang via `./flow run`, three runs:

| Allocator | Total | Per allocation |
|---|---|---|
| `malloc` + `free` per block | 2.23 - 2.33 ms | 11.2 - 11.6 ns |
| `frame_alloc_f32`, one `frame_begin` per frame | 1.108 - 1.110 ms | 5.54 - 5.55 ns |

About 2.1x per allocation, against a `malloc` that is hitting its best case:
same size every time, freed immediately, so the allocator's fast path is warm.
The ratio is the durable part; the absolute numbers are one machine.

The larger difference is not in that table. The malloc column pays 200,000
frees. The frame column pays 200 stores of zero, one per `frame_begin`, and
the cost of releasing a frame does not grow with the number of allocations in
it. Bounded reset time is the reason the domain exists.

Run it with `FLOW_HOST=python ./flow run benchmarks/micro/frame_arena_benchmark.flow`.
The benchmark inlines its own copy of `FrameArena` so it stays one
translation unit.

## Example

[`examples/audio/lifetime_domains.flow`](../../examples/audio/lifetime_domains.flow)
is a full prep / process / teardown split: `application` statics for the run
counters, `@lifetime(session)` functions that do the only two `malloc`s,
an `@lifetime(frame)` block builder that bumps scratch for two voices, and
`@lifetime(callback)` render and mix functions that touch pre-allocated
storage only. It runs:

```text
blocks processed: 64
arena high water: 1024 bytes (one block's scratch)
peak level:       0.700
```

Move a `malloc` into `process_block` and the build stops:

```text
error: lifetime domain violation: 'process_block' is in the `frame` domain but
       calls 'malloc', which allocates or frees heap memory. Frame-domain code
       allocates by bumping a frame arena (frame_alloc_*); see
       docs/language/lifetime-domains.md
```

## Staging

| Capability | Status |
|---|---|
| `@lifetime(...)` on a function | ✅ |
| `@lifetime(...)` on a module static | ✅ (only attribute allowed there) |
| LD1 escape into a longer-lived static | ✅ direct cases — see [gaps](#what-the-compiler-does-not-check) |
| LD2 escape by return | ✅ direct cases |
| LD3 `callback` = `@rt_safe` | ✅ shares the `@rt_safe` call graph |
| LD3 `frame` forbids heap create/destroy | ✅ allocation names only, locks allowed |
| LD4 call ordering between declared domains | ✅ |
| `FrameArena` bump API in the stdlib | ✅ `lib/stdlib/memory.flow` |
| Escape through a call, struct field, closure or heap | ❌ not checked, by design in v0 |
| Domain of arena-allocated memory | ❌ |
| Domains on parameters / in types | ❌ |
| `request` / `persistent` domains | ❌ |
| `domain frame { ... }` blocks | ❌ |
| Domains in the MLIR / JS / Python backends | n/a — the annotation is checked, then erased |

The annotation leaves no trace in generated code. Every domain lowers to the
same C as the unannotated function.

## Future work

- `request` and `persistent` domains from Axiom §7.
- `domain frame { ... }` blocks that imply `frame_begin` / `frame_end`.
- Domains on parameters and in types (`ptr<f32> @ frame`), which is what would
  close the escape-through-a-call gap.
- Domain of arena-allocated memory, so a pointer from a frame arena carries
  `frame` rather than nothing.
- Cross-module domain checking.
- Lowering defaults: choosing stack, arena or heap automatically from the
  domain rather than from the call the programmer wrote.

## Related

[rt-safety.md](../library/rt-safety.md) · [memory.md](../library/memory.md) ·
[spans.md](spans.md) · [LANGUAGE_SPEC §8.4](../LANGUAGE_SPEC.md#84-lifetime-domains)

Tests: `tests/unit/test_lifetime_domains.py`,
`tests/lang/test_lifetime_domains.flow`
