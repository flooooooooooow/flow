# Lifetime domains

> **Status:** implemented in the C-backend type checker. `@lifetime(...)` may annotate functions and module statics. The compiler enforces direct escape, allocation-discipline, and domain-call-order rules.

A lifetime domain states how long storage is intended to remain valid:

| Domain | Typical lifetime |
|---|---|
| `callback` | one audio/render callback |
| `frame` | one frame or iteration |
| `session` | one document/stream/connection |
| `application` | the process lifetime |

The order is `callback < frame < session < application`. A longer-lived domain may not hold a reference to shorter-lived storage.

Every `flow` block on this page is compiler-checked in CI. Examples that are supposed to fail use `flow expect-error` and therefore also remain tested.

## Declaring domains

```flow
@lifetime(application)
let mut cache: ptr<i32> = null

@lifetime(callback)
function process_block(n: i32) -> i32 {
    return n
}
```

An unannotated function has no declared domain; the lifetime-domain rules are opt-in.

## LD1: a shorter-lived reference may not escape into longer-lived storage

```flow expect-error
let mut tail: span<f32> = null

@lifetime(callback)
function process() -> void {
    let scratch: array<f32, 4> = [0.0, 0.0, 0.0, 0.0]
    tail = scratch[0..4]
}
```

The compiler reports that `scratch` lives in `callback` while `tail` lives in `application`.

A pointer escape is rejected for the same reason:

```flow expect-error
let mut pointer_cache: ptr<i32> = null

@lifetime(frame)
function build_pointer() -> void {
    let scratch: array<i32, 4> = [1, 2, 3, 4]
    pointer_cache = &scratch
}
```

## LD2: a domain function may not return a reference into its own frame

```flow expect-error
@lifetime(frame)
function invalid_pointer() -> ptr<i32> {
    let scratch: array<i32, 8> = [0, 0, 0, 0, 0, 0, 0, 0]
    return scratch
}
```

The same rule applies to a span:

```flow expect-error
@lifetime(callback)
function invalid_span() -> span<i32> {
    let scratch: array<i32, 3> = [1, 2, 3]
    return scratch[0..3]
}
```

Returning a view of caller-owned storage is valid:

```flow
@lifetime(callback)
function head(values: span<i32>) -> span<i32> {
    return values[0..2]
}
```

## LD3: allocation discipline

`callback` composes with the real-time safety checker. Heap allocation and other forbidden operations are rejected on the callback call graph.

```flow expect-error
extern {
    function malloc(size: i64) -> ptr<void>
}

@lifetime(callback)
function invalid_callback(n: i32) -> i32 {
    let p: ptr<void> = malloc(64)
    return n
}
```

The `frame` domain permits bump allocation through the frame arena but rejects creation/destruction/growth operations that reach the general heap. `session` and `application` do not add allocation restrictions.

## LD4: a shorter-lived domain may not call into a longer-lived one

```flow expect-error
@lifetime(session)
function reload_preset(id: i32) -> i32 {
    return id
}

@lifetime(callback)
function invalid_call(n: i32) -> i32 {
    return reload_preset(n)
}
```

The opposite direction is valid: longer-lived orchestration may invoke shorter-lived callback work.

```flow
@lifetime(callback)
function render_sample(x: i32) -> i32 {
    return x + 1
}

@lifetime(session)
function run_session(x: i32) -> i32 {
    return render_sample(x)
}
```

## Interaction with spans

Span escape checking is always active for direct local-storage escapes. Lifetime domains generalise the same analysis to named domains and pointer-typed targets. When both checks apply, the domain diagnostic takes precedence because it contains more information.

## Frame arenas

A frame arena resets in bounded time and serves bump allocations without one free per allocation. The hot-path model is `frame_begin`, one or more `frame_alloc_*` calls, then `frame_end`. Creation and destruction stay outside the real-time path.

The complete shipped example is [`examples/audio/lifetime_domains.flow`](../../examples/audio/lifetime_domains.flow).

```bash
FLOW_HOST=python ./flow run examples/audio/lifetime_domains.flow
```

## Known gaps

The current checker intentionally does not claim whole-program ownership inference. It does not soundly follow references through arbitrary calls, struct fields, closures, indirect dispatch, heap objects, pointer laundering, or cross-module domain metadata. Arena-allocated memory also carries the caller-visible pointer type rather than a first-class arena domain.

These are documented gaps rather than partially enforced promises.

## Staging

| Capability | Status |
|---|---|
| `@lifetime(...)` on functions | ✅ |
| `@lifetime(...)` on module statics | ✅ |
| LD1 direct escape into longer-lived static | ✅ |
| LD2 direct return escape | ✅ |
| LD3 callback real-time restrictions | ✅ |
| LD3 frame heap-create/destroy restrictions | ✅ |
| LD4 domain call ordering | ✅ |
| FrameArena bump allocation | ✅ |
| Escape through arbitrary calls/fields/closures/heap | ❌ |
| First-class arena allocation domains | ❌ |
| `request` / `persistent` domains | ❌ |

The annotation is a compile-time property and is erased from generated code.

Related: [Spans](spans.md), [RT safety](../library/rt-safety.md), [Memory](../library/memory.md).
