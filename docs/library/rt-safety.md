# Real-Time Safety Policy (Audio)

Contract for code that runs on the **audio / callback thread** (or any path that must meet a hard deadline). Flow does not yet enforce this at compile time — treat it as a hard coding policy.

> [!important] No heap on the audio thread
> Allocate, free, open devices, and load assets **before** `audio_device_start` (or outside the process callback). The realtime path may only touch pre-allocated memory.

## Thread model

| Phase | Thread | Role |
|-------|--------|------|
| Setup / teardown | Main (or worker) | Open device, size buffers, init graphs, allocate delay lines / arenas |
| Process | Audio callback | Read/write samples, run filters/graphs, pull control values |
| Control | Main / UI / MIDI | Mutate parameters via atomics, lock-free queues, or double-buffered state |

The I/O layer (`stdlib/audio/io.flow` + `runtime/audio_*.c`) uses ring buffers so Flow user code does not register a C function pointer; the same deadline rules still apply to anything that fills or drains those buffers under load.

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
| `malloc` / `calloc` / `realloc` / `free` / `alloc_*` | Unbounded latency, fragmentation, locks |
| `arena_create` / growing arenas | Same as heap; prefer `arena_reset` of a prep-allocated arena **off** the callback if used at all |
| `audio_buffer_alloc_*`, delay-line create/resize | Setup-only |
| `audio_device_open` / `start` / `stop` / `close` | Syscalls and driver work |
| File, network, GPU submit, Metal/CUDA allocate | Blocking / jitter |
| Unbounded locks, `mutex`, waiting on UI | Priority inversion, glitches |
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
