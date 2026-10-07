# Lifetime domains

> **Status:** v0 is implemented in the C-backend type checker. Domains are
> declared with `@lifetime(...)` on functions, module statics, and struct
> fields. Five rules are enforced (see
> [What the compiler checks](#what-the-compiler-checks)). Composite stores
> through fields and collections are [domain-fields.md](domain-fields.md)
> (issue #684). Everything the checker cannot decide soundly is listed under
> [What the compiler does not check](#what-the-compiler-does-not-check) and is
> not half-checked.

A real-time program does not have one memory. It has several, each with a
different clock:

| Domain | Lives for | Typical storage |
|---|---|---|
| `callback` | one audio block or one render callback | stack locals, caller-provided buffers |
| `frame` | one frame of a loop | a bump arena, reset wholesale at the frame boundary |
| `request` | one HTTP, RPC, or event request | per-request heap or a request arena |
| `session` | one document, one stream, one connection | pooled or resettable region |
| `application` | the whole process run | module statics, long-lived heap |
| `persistent` | durable store that outlives this process run | files, mmap, a database handle |

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
callback  <  frame  <  request  <  session  <  application  <  persistent
```

Read `<` as "lives no longer than". A `callback` value is dead by the time the
next block starts. An `application` value is alive until the process exits.
`request` sits between a frame and a session: one inbound HTTP, RPC, or event
is longer than a render frame and shorter than the connection that produced
it. `persistent` is longer than this process run, so a persistent static must
be TransportSafe and holds no pointer at all (#1421).

The single rule the whole design rests on:

> A longer-lived domain may not hold a reference to a shorter-lived one.

## Declaring a domain

`@lifetime(D)` on a function declares the domain its frame runs in:

```flow-pseudocode
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

`request` and `persistent` use the same attribute. A request handler may
allocate; a persistent static is the longest-lived storage:

```flow-pseudocode
@lifetime(request)
function handle(id: i32) -> i32 { return id }

@lifetime(persistent)
let mut hits: i32 = 0
```

`@lifetime(D)` on a struct field declares the domain of the storage that
field may point to, wherever the instance lives. See
[domain-fields.md](domain-fields.md) (LD5).

Those are the only three places a domain is written. This is the
"annotation-only" answer to the open question in the issue: no `domain frame
{ ... }` blocks, no per-`let` annotations, no domains in types. See
[project Questions](../project/Questions.md).

## How a value gets its domain

Inferred from its allocation site. Nothing else.

| Storage | Domain |
|---|---|
| a local declared in a `@lifetime(D)` function | `D` |
| a local declared in an unannotated function | none (unchecked) |
| a module static | its `@lifetime(...)`, defaulting to `application` |
| a `const` | `application` |
| memory from `malloc` / `alloc_*` | `application` (it is yours until you free it) |
| memory from `arena_alloc` / `frame_alloc_*` | the arena instance's declared domain when that instance is a module static; otherwise the writing function's domain (the v0 writer-domain rule) |

An unannotated function has no domain, so no domain rule fires inside it. The
whole feature is opt-in; adding `@lifetime(...)` to one function does not
change the meaning of any other.

## What the compiler checks

Five rules. Each one is a hard error in `--strict` and a printed warning in
`--lenient`, like every other type-checker diagnostic.

### LD1: a shorter-lived value may not be stored in a longer-lived static

Inside a `@lifetime(D)` function, assigning a reference rooted in
function-local storage to a module static whose domain outlives `D`:

```flow expect-error
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

When the stored value is memory bumped from a *module-static* arena
(`arena_alloc` / `frame_alloc_*`, argument written `arena` or `&arena`),
the pointer carries that arena's own declared `@lifetime(D)` rather than
the writing function's domain. The rule is provable from the arena
declaration alone, so it fires even from a function that declares no
domain. An unannotated static arena defaults to `application` and never
outlives a target. An arena reached only through a parameter or a local
keeps the writer-domain rule above. That is how a frame or session arena
is stopped from escaping past the reset that ends its domain.

Module statics are `ptr<Arena>` / `ptr<FrameArena>` today (value-typed
struct statics are not representable); both `arena` and `&arena` name the
same instance when the static is the arena record itself:

```flow expect-error
@lifetime(frame)
let mut fa: ptr<Arena> = null

@lifetime(application)
let mut cache: ptr<void> = null

function build() -> void {
    cache = arena_alloc(fa, 64)
}
```

```text
error: lifetime domain escape: `fa` lives in the `frame` domain but is
       stored in `cache`, which lives in the `application` domain (a
       longer-lived domain may not hold a reference to a shorter-lived
       one) at line 12, column 5
```

`malloc` / `alloc_*` are unchanged: they have no arena instance, so they
stay `application` and this rule does not apply to them.

### LD2: a domain function may not return a reference into its own frame

```flow expect-error
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

### LD3: allocation discipline per domain

`@lifetime(callback)` composes with `@rt_safe`: the body, and everything it
calls transitively, must not touch the heap, take a blocking lock, open a
device or file, or submit GPU work. The check is the existing `@rt_safe`
whole-program call graph, so nothing new can slip past it that `@rt_safe`
would have caught.

```flow expect-error
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

`request`, `session`, `application` and `persistent` place no allocation
restriction. A request handler may `malloc`; a frame or callback may not.

### LD4: a domain may not call into a longer-lived domain

Both functions must be annotated for this to fire. It checks declared intent
against declared intent, so it has no false positives on unannotated code.

```flow expect-error
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

### LD5: a shorter-lived reference may not be stored in a longer-lived field

LD1 covers module statics. LD5 extends the same rule to composite storage
([domain-fields.md](domain-fields.md), issue #684). A store `base.field = value`
is an escape when the field's domain outlives the writing frame and `value`
is rooted in that frame.

A field's domain comes from one of two places:

- **The static it belongs to.** A reference stored anywhere inside a module
  static, at any field depth or through an array element, takes the static's
  domain. `holder.inner.view = &scratch` and `table[0] = &scratch` are both
  caught when `holder` and `table` are statics. A struct or array literal
  assigned to that static is walked the same way.
- **An `@lifetime(D)` on the field itself.** The annotation is a contract that
  the field holds a `D`-domain reference, so a shorter-lived store breaks it
  wherever the struct instance lives:

```flow expect-error
struct Holder {
    @lifetime(application)
    view: ptr<i32>
}

@lifetime(callback)
function process() -> void {
    let mut h: Holder = Holder { view: null }
    let scratch: array<i32, 4> = [1, 2, 3, 4]
    h.view = &scratch
}
```

```text
error: lifetime domain escape: `scratch` lives in the `callback` domain but is
       stored in field `view`, which is declared to live in the `application`
       domain (a longer-lived domain may not hold a reference to a
       shorter-lived one) at line 11, column 5
```

Both halves are opt-in. A store fires only when the writing function declares a
domain, the field's domain outlives it, and the value is rooted in the writing
frame. An unannotated field on a local struct is left alone, because a local
struct dies with the frame and receives no longer-lived promise.

## What the compiler does not check

A lifetime system that misses violations is worse than no lifetime system,
because people trust it. Everything below compiles today and is **not**
checked. None of it is partially checked.

- **Escape through an unannotated field of a struct whose lifetime is not
  known.** Two field cases are checked (see LD5): a store into any field
  or element of a module static, and a store into a field declared with
  `@lifetime(D)`. A store into a plain field of a struct reached only through a
  pointer parameter is still not tracked, because the checker cannot prove that
  struct outlives the writing frame. Copying a previously-filled local struct
  onto a longer-lived location without a literal on the right-hand side is
  also not tracked.
- **Escape through a closure environment**, a function pointer, or dynamic
  dispatch. The `@rt_safe` call graph is over direct named calls only, and LD3
  and LD4 inherit that.
- **Use after `arena_reset` / `frame_begin` in the same function.** A
  pointer produced before a reset of the same arena is not invalidated
  by the reset call. The checker stops the pointer escaping into a
  longer-lived static (the domain boundary *is* the reset boundary);
  intra-function use-after-reset is not tracked.
- **Escape through the heap.** `*p = &local` where `p` is `malloc`'d is
  application-domain storage receiving a callback-domain reference, and is not
  caught. A module-static arena stored into a longer-lived static *is*
  caught (LD1 plus #690); a `malloc`'d cell is not an arena instance.
- **Pointer laundering.** Casts, integer round-trips, and pointer arithmetic
  that leaves the tracked expression shapes (variable, slice, address-of,
  field/index under address-of).
- **Extern functions.** An `extern` C call is assumed to have no domain. A
  known RT-unsafe name (heap, lock, device/file I/O) is recorded on its
  compact summary; any other extern carries an explicit `unknown` bit
  rather than an empty summary. This slice still rejects only the known
  unsafe names from `@rt_safe` / `callback`, matching the previous
  allow-list. Tightening `unknown` is future work.
- **Cross-module domains.** Public functions emit a compact effect/lifetime
  summary (`$fname` in the module effect table): callback-safe / frame-safe
  bits, may allocate/free, may block/lock, may do device/file/network I/O,
  declared lifetime domain, and one provenance edge per newly introduced
  bit. Importers consult that summary as a leaf during type checking
  ([#765](https://github.com/flooooooooooow/flow/issues/765)). The
  annotation is still erased before codegen.

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

The two share their remaining gaps: neither follows a borrow through a
call or a closure. Domain checking does follow a borrow through a
static-rooted field path, an annotated field, and a struct or array
literal. See [spans.md § Lifetime](spans.md#lifetime) and
[domain-fields.md](domain-fields.md).

## Frame domain and the arena

The `frame` domain is wired to the existing bump allocator in
`lib/stdlib/memory.flow`. A `FrameArena` is an `Arena` plus frame bookkeeping:

```flow-pseudocode
export struct FrameArena {
    arena: Arena,
    high_water: i64,
    frames: i64
}
```

The API is three calls in the hot path, all bump-pointer arithmetic and all
legal in `callback` and `frame`:

```flow-pseudocode
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

Run it with `./flow run benchmarks/micro/frame_arena_benchmark.flow`.
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
| LD1 escape into a longer-lived static | ✅ direct cases and composite stores; see [gaps](#what-the-compiler-does-not-check) |
| LD2 escape by return | ✅ direct cases and struct/array literals |
| LD3 `callback` = `@rt_safe` | ✅ shares the `@rt_safe` call graph |
| LD3 `frame` forbids heap create/destroy | ✅ allocation names only, locks allowed |
| LD4 call ordering between declared domains | ✅ |
| `FrameArena` bump API in the stdlib | ✅ `lib/stdlib/memory.flow` |
| LD1 escape into a struct field or collection of a longer-lived static | ✅ [domain-fields.md](domain-fields.md) |
| LD5 `@lifetime(D)` on a struct field | ✅ [domain-fields.md](domain-fields.md) |
| Escape through a call, closure or heap | ❌ not checked, by design in v0 |
| Domain of arena-allocated memory | ✅ module-static `arena_alloc` / `frame_alloc_*` carry the arena's `@lifetime` (#690) |
| Domains on parameters / in types | ❌ |
| `request` / `persistent` domains | ✅ |
| `domain frame { ... }` blocks | ❌ |
| Domains in the MLIR / JS / Python backends | n/a: the annotation is checked, then erased |
| Cross-module summaries for public functions | ✅ first slice (#765): bitset + domain + one provenance edge |
| Cross-module `unknown` externs rejected from `@rt_safe` | ❌ recorded on the summary; not yet a hard error |

The annotation leaves no trace in generated code. Every domain lowers to the
same C as the unannotated function.

## Future work

- `domain frame { ... }` blocks that imply `frame_begin` / `frame_end`.
- Domains on parameters and in types (`ptr<f32> @ frame`), which is what would
  close the escape-through-a-call gap.

- Reject the `unknown` summary bit from `@rt_safe` / `callback` once
  a known-safe extern allow-list exists.
- Lowering defaults: choosing stack, arena or heap automatically from the
  domain rather than from the call the programmer wrote.

## Related

[rt-safety.md](../library/rt-safety.md) · [memory.md](../library/memory.md) ·
[spans.md](spans.md) · [region-inference.md](region-inference.md) ·
[domain-fields.md](domain-fields.md) ·
[request and persistent](lifetime-request-persistent.md) ·
[LANGUAGE_SPEC §8.4](../LANGUAGE_SPEC.md#84-lifetime-domains)

Tests: `compiler/fixtures/typecheck_rules/domain_*.flow`,
`tests/lang/test_lifetime_domains.flow`,
`tests/lang/test_arena_domains.flow`,
`tests/lang/test_lifetime_request_persistent.flow`,
`tests/lang/test_domain_fields.flow`
