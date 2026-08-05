# Real-Time Safety Policy (Audio)

Contract for code that runs on the **audio / callback thread** (or any path that must meet a hard deadline).

> [!important] No heap on the audio thread
> Allocate, free, open devices, and load assets **before** `audio_device_start` (or outside the process callback). The realtime path may only touch pre-allocated memory.

## Compile-time enforcement: `@rt_safe`

Mark a function with the `@rt_safe` attribute to have the type checker reject
any call — direct or transitive — from that function into a heap-touching
API:

```flow
@rt_safe
function process_block(state: ptr<FilterState>, block_size: i32) -> void {
    let mut i: i32 = 0
    while i < block_size {
        # filter math over pre-allocated state only
        i = i + 1
    }
}
```

`@rt_safe` uses Flow's existing decorator syntax (like `@gpu`, `@inline`,
`@only(...)`) rather than a comment pragma, since the parser already
supports attributes on `function` declarations.

**What's checked today** (`src/flow/type_checker.py`):

- Direct calls to `malloc`, `calloc`, `realloc`, `free` (and the generic
  `alloc`/`dealloc` builtins) from an `@rt_safe` function are a type error.
- Direct calls to `lib/stdlib/memory.flow` helpers that wrap those primitives
  — `alloc_bytes`, `alloc_zeroed`, `alloc_i32`, `alloc_f32`, `alloc_f64`,
  `arena_create`, `arena_destroy` — are a type error.
- **Transitive** calls are also caught: if an `@rt_safe` function calls a
  helper that (however indirectly) calls one of the names above, that's a
  type error too. The checker builds a whole-module call graph and reports
  the first heap-touching call in the chain.
- Bump allocation from an *already-created* arena is allowed: `arena_alloc`,
  `arena_alloc_i32`, `arena_alloc_f32`, `arena_reset`, `arena_used`, and
  `arena_remaining` never call `malloc`/`free` themselves, so they stay
  RT-safe. Only creating or destroying the arena's backing storage
  (`arena_create` / `arena_destroy`) is forbidden — do that in prep/teardown
  and pass the live `Arena` into the `@rt_safe` path.
- This runs in both `--strict` (error, exit 1) and `--lenient` (printed
  warning, compiles anyway) modes, matching every other type-checker
  diagnostic.

**Known gaps** (not yet enforced — still a coding policy for these):

- Calls through function pointers / closures aren't traced, only direct
  named calls.
- Method calls (`obj.method(...)`) aren't checked against the heap-name
  list, only plain function calls — not an issue for `memory.flow` today
  since it exposes free functions, not methods.
- `extern` C calls other than the malloc family aren't assumed to allocate
  (e.g. a hypothetical `extern` audio driver call could allocate internally
  without the checker knowing).
- Device/file/network calls (`audio_device_open`, syscalls, GPU submit) are
  still policy-only, not name-checked.
- No enforcement for unbounded loops or unbounded `printf` — those remain a
  review-time concern.
- **Locks are compile-time checked:** `pthread_mutex_lock` /
  `pthread_cond_wait` / `pthread_rwlock_rdlock` / `pthread_rwlock_wrlock` /
  Flow `mutex_lock` / `condvar_wait` / `rwlock_rdlock` / `rwlock_wrlock` /
  `semaphore_wait` / `sem_wait` (and transitive wrappers) are rejected inside
  `@rt_safe` with a “may block / priority inversion” diagnostic. Blocking
  channel ops (`channel_i32_send` / `recv` / `select2`) are not yet name-checked.

## Thread model

| Phase | Thread | Role |
|-------|--------|------|
| Setup / teardown | Main (or worker) | Open device, size buffers, init graphs, allocate delay lines / arenas |
| Process | Audio callback | Read/write samples, run filters/graphs, pull control values |
| Control | Main / UI / MIDI | Mutate parameters via atomics, lock-free queues, or double-buffered state |

The I/O layer (`stdlib/audio/io.flow` + `runtime/audio_miniaudio.c`) uses an SPSC
ring whose hot path is Flow (`lib/runtime/audio_spsc.flow` over `flow_atomic_*`) so
user code does not register a C function pointer; the same deadline rules still
apply to anything that fills or drains those buffers under load. No heap, locks,
or blocking waits inside the ring ops.

## Allowed on the audio thread

- Arithmetic, branches, fixed-bound loops over a known block size
- Stack locals and pre-sized `array<T, N>` / caller-provided buffers
- In-place DSP: filters, oscillators, delay lines with storage allocated at init
- Fixed-size graphs (`graph_scheduler`, `graph_bus`) once nodes/buffers exist
- SIMD helpers that do not allocate (`stdlib/audio/simd.flow`)
- Lock-free / atomic parameter reads (or one-writer control smoothing)
- `printf`-style logging only in **debug** builds — never in shipping realtime paths

## Forbidden on the audio thread

| Forbidden | Why |
|-----------|-----|
| `malloc` / `calloc` / `realloc` / `free` / `alloc_*` | Unbounded latency, fragmentation, locks — **compile-time checked** in `@rt_safe` functions |
| `arena_create` / growing arenas | Same as heap; prefer `arena_reset` of a prep-allocated arena **off** the callback if used at all — **compile-time checked** in `@rt_safe` functions |
| `audio_buffer_alloc_*`, delay-line create/resize | Setup-only |
| `audio_device_open` / `start` / `stop` / `close` | Syscalls and driver work |
| File, network, GPU submit, Metal/CUDA allocate | Blocking / jitter |
| Unbounded locks, `mutex`, `cond_wait`, waiting on UI | Priority inversion, glitches — **compile-time checked** for known lock/wait names in `@rt_safe` |
| Dynamic string formatting / unbounded `printf` in release | Allocation and I/O |
| Resizing graphs, hot-loading plugins mid-callback without a prep stage | Hidden allocation and races |

## Prep vs process checklist

1. **Prep (non-RT):** open device → allocate buffers / delay storage → `audio_graph_init` (or equivalent) → start device.
2. **Process (RT):** for each block, process into existing buffers; read control values; never grow structures.
3. **Teardown (non-RT):** stop device → free everything.

## Stdlib guidance

| Module | RT notes |
|--------|----------|
| `audio/filters.flow`, `oscillators.flow`, `control.flow` | Process-safe once state exists |
| `audio/delay_line.flow` | Create/resize off-thread; `process` on-thread |
| `audio/graph*.flow` | Fixed capacity; init before start |
| `audio/io.flow` | Open/start/stop off-thread; read/write under deadline |
| `audio/gpu.flow` | Not RT-safe for allocate/submit unless a dedicated non-blocking design is used |
| `stdlib/memory.flow` | Heap APIs are **setup-only** on audio paths |

## Related

- [Audio DSP](audio.md) — modules and I/O backends
- [Memory](memory.md) — heap and arenas (use only in prep/teardown for RT apps)
- Examples: `examples/audio/loopback_effects.flow`, `examples/audio/bus_graph_demo.flow`
- Tests: `tests/unit/test_rt_safety.py` — `@rt_safe` positive/negative cases
