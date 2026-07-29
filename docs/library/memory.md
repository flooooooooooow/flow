# Manual Memory Management

Flow has **no garbage collector**. Heap memory is allocated and freed explicitly — same contract as C, with typed helpers and an arena bump allocator in `lib/stdlib/memory.flow`.

> [!important] Ownership is yours
> Every successful `malloc` / `calloc` / `alloc_*` must be paired with `free`, or owned by an arena you later `arena_destroy`.

## Quick start

```flow
import "stdlib/memory.flow"

function main() -> i32 {
    let nums: ptr<i32> = alloc_i32(4)   # calloc'd i32[4]
    if nums == null {
        printf("out of memory\n")
        return 1
    }
    nums[0] = 10
    nums[1] = 20
    printf("%d %d\n", nums[0], nums[1])
    free(nums)
    return 0
}
```

Run: `./flow run your_file.flow`

## API surface

### libc heap (FFI)

| Function | Role |
|----------|------|
| `malloc(size)` | Uninitialized bytes → `ptr<void>` or `null` |
| `calloc(n, size)` | Zeroed `n * size` bytes |
| `realloc(p, size)` | Grow/shrink (may move) |
| `free(p)` | Release (`null` is a no-op) |

### Typed helpers

| Function | Role |
|----------|------|
| `alloc_bytes` / `alloc_zeroed` | Byte slabs |
| `alloc_i32` / `alloc_f32` / `alloc_f64` | Zeroed typed arrays |
| `memory_zero_i32` / `memory_copy_i32` | Element loops (no libc `memcpy` clash) |
| `sizeof_*` / `alignof_*` / `align_up` / `align_down` | Layout helpers |

### Arena (bump allocator)

| Function | Role |
|----------|------|
| `arena_create(cap)` | One `malloc` slab |
| `arena_alloc` / `arena_alloc_i32` / `arena_alloc_f32` | Bump allocate (8-byte aligned) |
| `arena_reset` | Reuse slab without freeing |
| `arena_destroy` | `free` the slab |
| `arena_used` / `arena_remaining` | Bookkeeping |

```flow
import "stdlib/memory.flow"

function main() -> i32 {
    let mut a: Arena = arena_create(4096)
    let xs: ptr<i32> = arena_alloc_i32(&a, 128)
    let ys: ptr<f32> = arena_alloc_f32(&a, 128)
    # … use xs / ys …
    arena_destroy(&a)   # frees everything from this arena
    return 0
}
```

## Rules of thumb

1. **Check for `null`** after every heap allocation.
2. **One free per malloc** — double-free and use-after-free are undefined behaviour (same as C).
3. **Arenas for frames** — audio blocks, request handlers, parsers: allocate freely, destroy once.
4. **Stack first** — fixed arrays and locals need no `free`.
5. **Don't free arena pointers individually** — only `arena_destroy` / `arena_reset`.

## Tutorials

- [Memory tutorial](../tutorials/memory.md) — malloc, typed alloc, arenas, patterns
- [Pointers tutorial](../tutorials/pointers.md) — `ptr<T>`, indexing, null
- [Systems tutorial](../tutorials/systems.md) — pools, buffers, ring-style patterns

## See also

- [RT Safety](rt-safety.md) — no-alloc audio-thread contract
- [Comparison](../comparison.md) — Flow vs C/Rust memory models
- Working demo: `examples/systems/manual_memory.flow`
