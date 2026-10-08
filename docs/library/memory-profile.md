# Runtime memory profile

Compiled programs include an opt-in allocator profile (#740). It is dormant
unless `FLOW_MEM_PROFILE` is set to a non-empty value other than `0` when
the process starts: one predictable branch per routed allocation and no
output otherwise.

This page is the report contract. Manual allocation APIs stay on
[Memory](memory.md). Static lifetime analysis is a separate track (#669)
and is not implemented by these counters.

## Enabling

When enabled, the program writes a report at exit to stderr, or to the file
named by `FLOW_MEM_PROFILE_OUT`.

`./flow tool bench_harness` sets both variables for every measured subject,
so the #728 schema records `allocations`, `heap_bytes`, `peak_live_heap`,
`temp_bytes`, `copies`, `copy_count` and `median_rss_kb` without rewriting workload
sources.

## Counters

Human lines and parseable `key: value` lines are both written:

| Parseable key | Meaning |
|---|---|
| `allocations` | Routed heap allocation count |
| `heap_bytes` | Cumulative bytes requested from the heap |
| `peak_live_heap` | High-water mark of still-live routed heap bytes |
| `peak_rss_kb` | Peak RSS via `getrusage` (macOS bytes are normalised) |
| `temp_bytes` | Compiler-temporary bytes (string concat / format helpers) |
| `copies` | Copy volume from routed `memcpy` and attributed compiler copies |
| `copy_count` | Copy operations: routed `memcpy`, string joins and compiler-emitted aggregate copies (#732) |
| `stack_bytes` | Compiler-placed stack storage (sized arrays, sort scratch, MLIR alloca) |
| `arena_bytes` | Successful `arena_alloc` / `frame_alloc` bump bytes |
| `promotion_bytes` | `stack_bytes + arena_bytes` |
| `live_map_used` | Occupied slots in the capped live-block map |
| `live_map_overflow` | Puts that did not fit; frees of those pointers may not shrink live bytes |
| `site_heap` | Bytes attributed to user/heap wrappers |
| `site_temp` | Compiler-temporary site |
| `site_concat` | String-join copies |
| `site_sort` | Sort scratch copies / notes |
| `site_array` | Sized-array copies |
| `site_copy` | Other routed `memcpy` |
| `site_stack` | Stack promotion events |
| `site_arena` | Arena bump events |

## Live-block map

Peak live heap needs the size of each still-live pointer. The runtime keeps
a **capped open-addressing map** (4096 slots, hashed, tombstones on take).
Overflow still counts the allocation toward `allocations` / `heap_bytes` /
`peak_live_heap`, but a later `free` of an overflowed pointer cannot find
the size. `live_map_overflow` makes that under-count visible.

## Backends

The C backend emits the full prelude in every program. The MLIR backend
emits matching `flow_mem_*` wrappers and counters when the module uses
malloc, memcpy, free, string helpers, or stack promotion, and rewrites
those call sites.

## Related

[Memory](memory.md), [Lifetime domains](../language/lifetime-domains.md),
[RT safety](rt-safety.md).
