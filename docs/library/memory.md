# Manual Memory Management

Flow has no garbage collector. Heap memory is allocated and freed explicitly, with typed helpers and arena allocators in `lib/stdlib/memory.flow`. Every `flow` block on this page is compiler-checked in CI.

For GPU/unified storage see [GPU memory](gpu-memory.md).

## Heap quickstart

```flow
import "stdlib/memory.flow"

function main() -> i32 {
    let nums: ptr<i32> = alloc_i32(4)
    if nums == null {
        return 1
    }
    nums[0] = 10
    nums[1] = 20
    let result: i32 = nums[0] + nums[1]
    free(nums)
    return result - 30
}
```

Every successful heap allocation must be released exactly once unless ownership is transferred to an arena or another explicit owner.

## API surface

The libc layer exposes `malloc`, `calloc`, `realloc`, and `free`. Typed helpers include `alloc_bytes`, `alloc_zeroed`, `alloc_i32`, `alloc_f32`, `alloc_f64`, memory copy/zero helpers, and layout helpers.

## Allocation failure and integer overflow

Heap allocators, typed allocations and both arenas reject non-positive
requests, invalid element counts and byte counts that overflow `i64`.
They return `null` and never call libc with a negative size or a wrapped
`count * sizeof(T)`. `align_up` returns `-1` when the alignment is not a
positive power of two, the size is negative, or the rounded size would
overflow `i64`.

The frame allocator checks `0 <= offset <= capacity` and then
`rounded_bytes <= capacity - offset`, so it never computes an
overflowing `offset + rounded_bytes`. A rejected allocation leaves the
arena offset, the frame high-water mark and the frame count unchanged.
The checks do not allocate, so they are safe on callback paths.

`grow_uninit(p, 0)` and `grow_zeroed(p, old, 0)` return `null` and leave
`p` owned by the caller. `grow_zeroed` also requires `old_size >= 0`, and
`old_size == 0` when `p` is null, so a new region cannot skip zeroing. A
failed `realloc` leaves the original pointer owned by the caller.

`tests/lang/test_memory_bounds.flow` covers these cases.

## Arena allocator

```flow
import "stdlib/memory.flow"

function arena_example() -> i32 {
    let mut arena: Arena = arena_create(4096)
    let xs: ptr<i32> = arena_alloc_i32(&arena, 128)
    let ys: ptr<f32> = arena_alloc_f32(&arena, 128)
    if xs == null or ys == null {
        arena_destroy(&arena)
        return 1
    }

    xs[0] = 42
    ys[0] = 0.5
    let result: i32 = xs[0]
    arena_destroy(&arena)
    return result - 42
}
```

An arena owns one backing slab; individual arena allocations are not freed separately. `arena_reset` reuses the slab and `arena_destroy` releases it.

A module-static `ptr<Arena>` or `ptr<FrameArena>` may carry `@lifetime(D)`.
Pointers returned by `arena_alloc` / `frame_alloc_*` from that instance
inherit `D`, so they cannot be stored in a longer-lived static (the
domain boundary is the reset boundary). See
[lifetime domains](../language/lifetime-domains.md).

## Frame arena

`FrameArena` adds per-frame reset and high-water accounting. The full example includes the library import and lifetime annotation it depends on:

```flow
import "stdlib/memory.flow"

@lifetime(frame)
function render_frame(frame: ptr<FrameArena>, n: i64) -> f32 {
    frame_begin(frame)
    let scratch: ptr<f32> = frame_alloc_f32(frame, n)
    if scratch == null {
        frame_end(frame)
        return -1.0
    }
    scratch[0] = 1.0
    let result: f32 = scratch[0]
    frame_end(frame)
    return result
}
```

Frame reset is bounded bump-pointer bookkeeping rather than one free per object. Creation/destruction remain startup/shutdown operations.

## Runtime memory profile

Compiled programs include an opt-in allocator profile (#740). It is dormant unless `FLOW_MEM_PROFILE` is set to a non-empty value other than `0` when the process starts: one predictable branch per routed allocation and no output otherwise.

When enabled, the program writes a report at exit to stderr, or to the file named by `FLOW_MEM_PROFILE_OUT`:

- heap allocation count and cumulative bytes requested
- peak live heap (high-water mark of still-live routed bytes)
- peak RSS via `getrusage` (kilobytes; macOS bytes are normalised)
- compiler-temporary bytes (string concat / format helpers)
- copy volume from routed `memcpy`, string joins, and compiler-emitted aggregate copies
- copy operation count (`copy_count`), the #732 metric wired into the #728 harness

`./flow tool bench_harness` sets both variables on the memory suite, so the #728 schema records `allocations`, `heap_bytes`, `peak_live_heap`, `temp_bytes`, `copies`, `copy_count` and `median_rss_kb` without rewriting workload sources. Runtime rows leave the profiler off so `flow_vs_native` is not the wrapper tax.

Stack/arena promotion bytes and per-source copy attribution are reported as deferred until the lifetime work in #669.

## Rules

Check allocations for `null`; prefer stack/fixed arrays when size is static; free heap allocations exactly once; do not individually free arena pointers; and use arenas when a whole set of transient objects has one natural reset point.

Working demo: [`examples/systems/manual_memory.flow`](../../examples/systems/manual_memory.flow). Related: [RT safety](rt-safety.md), [Lifetime domains](../language/lifetime-domains.md), and [Spans](../language/spans.md).
